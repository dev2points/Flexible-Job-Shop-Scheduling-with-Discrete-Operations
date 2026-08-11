import argparse
from collections import defaultdict
import re
import sys
from time import perf_counter
from pysat.solvers import Solver


def read_file(file_path):
    print(f"Reading file: {file_path}")
    SCO = []
    SFO = []

    try:
        with open(file_path, "r") as file:
            # 1. Đọc dòng đầu tiên chứa num_jobs và num_machines
            first_line = file.readline().strip()
            while not first_line or first_line.startswith("#"):
                first_line = file.readline().strip()

            first_tokens = [int(x) for x in re.findall(r"\d+", first_line)]
            num_jobs = first_tokens[0]
            num_machines = first_tokens[1]

            # Bỏ qua các dòng tiêu đề phụ nếu là file PFS
            if "×" in file_path.upper():
                file.readline()
                file.readline()

            # 2. Đọc dữ liệu từng Job
            for job_id in range(num_jobs):
                line = file.readline().strip()
                while not line or line.startswith("#"):
                    line = file.readline().strip()

                tokens = [int(x) for x in re.findall(r"\d+", line)]
                idx = 0

                num_operation_per_job = tokens[idx]
                idx += 1

                num_sco = tokens[idx]
                idx += 1

                # Đọc các thao tác SCO
                for sco_id in range(num_sco):
                    num_machine_per_operation = tokens[idx]
                    idx += 1

                    request_list = {}
                    for _ in range(num_machine_per_operation):
                        machine_id = (
                            tokens[idx] - 1
                        )  # Trừ 1 nếu muốn 0-indexed (0, 1, 2)
                        processing_time = tokens[idx + 1]
                        idx += 2
                        request_list[machine_id] = processing_time

                    SCO.append(
                        {
                            "job_id": job_id,
                            "op_id": sco_id,
                            "request_list": request_list,
                        }
                    )

                # Tính số lượng SFO
                num_sfo = num_operation_per_job - num_sco

                # Nếu có SFO, bỏ qua token khai báo số lượng SFO trong file (nếu có)
                if num_sfo > 0:
                    # Kiểm tra nếu token tiếp theo chính là số lượng SFO khai báo trong file
                    if tokens[idx] == num_sfo:
                        idx += 1

                    # Đọc các thao tác SFO
                    for sfo_offset in range(num_sfo):
                        sfo_id = num_sco + sfo_offset
                        num_machine_per_operation = tokens[idx]
                        idx += 1

                        request_list = {}
                        for _ in range(num_machine_per_operation):
                            machine_id = (
                                tokens[idx] - 1
                            )  # Trừ 1 nếu muốn 0-indexed
                            processing_time = tokens[idx + 1]
                            idx += 2
                            request_list[machine_id] = processing_time

                        SFO.append(
                            {
                                "job_id": job_id,
                                "op_id": sfo_id,
                                "request_list": request_list,
                            }
                        )

    except FileNotFoundError:
        print(f"Lỗi: Không tìm thấy file tại đường dẫn '{file_path}'")
        return None
    except Exception as e:
        print(f"Lỗi khi đọc file: {e}")
        return None
    print(f"Finished reading file: {file_path}")

    return num_jobs, num_machines, SCO, SFO


def greedy_schedule(num_jobs, num_machines, SCO, SFO):
   
    # 1. Gom nhóm thao tác theo từng Job
    job_scos = defaultdict(list)
    job_sfos = defaultdict(list)

    for op in SCO:
        job_scos[op['job_id']].append(op)
    for op in SFO:
        job_sfos[op['job_id']].append(op)

    # Đảm bảo SCO sắp xếp đúng thứ tự op_id tăng dần trong mỗi Job
    for j in job_scos:
        job_scos[j].sort(key=lambda x: x['op_id'])

    # 2. Khởi tạo trạng thái theo dõi thời gian rảnh
    job_free_time = defaultdict(int)       # Thời điểm Job j sẵn sàng thực hiện thao tác mới
    machine_free_time = defaultdict(int)   # Thời điểm Máy m rảnh
    job_sco_idx = {j: 0 for j in range(num_jobs)}  # Con trỏ SCO tiếp theo của từng Job

    schedule = []
    total_ops = len(SCO) + len(SFO)
    scheduled_count = 0

    # 3. Vòng lặp Greedy lên lịch cho từng thao tác
    while scheduled_count < total_ops:
        best_candidate = None
        best_finish_time = float('inf')
        best_start_time = float('inf')
        best_machine = None
        best_proc_time = None
        best_is_sco = False

        # Tìm các thao tác đang sẵn sàng (Candidates) từ tất cả các Job
        for j in range(num_jobs):
            candidates = []

            # SCO tiếp theo của Job j (nếu còn)
            if job_sco_idx[j] < len(job_scos[j]):
                candidates.append((job_scos[j][job_sco_idx[j]], True))

            # Tất cả SFO chưa thực hiện của Job j
            for sfo_op in job_sfos[j]:
                candidates.append((sfo_op, False))

            # Đánh giá tất cả các ứng viên trên từng máy khả thi
            for op, is_sco in candidates:
                for m, p_time in op['request_list'].items():
                    # Thời điểm bắt đầu khả thi = max(Job rảnh, Máy rảnh)
                    start = max(job_free_time[j], machine_free_time[m])
                    finish = start + p_time

                    # Ưu tiên chọn cặp (Thao tác, Máy) có thời gian hoàn thành sớm nhất
                    if finish < best_finish_time:
                        best_finish_time = finish
                        best_start_time = start
                        best_candidate = op
                        best_machine = m
                        best_proc_time = p_time
                        best_is_sco = is_sco

        # Gán lịch cho ứng viên tốt nhất được chọn
        if best_candidate is not None:
            j = best_candidate['job_id']
            op_id = best_candidate['op_id']

            # Cập nhật thời điểm rảnh của Job và Máy
            job_free_time[j] = best_finish_time
            machine_free_time[best_machine] = best_finish_time

            # Cập nhật danh sách chờ của Job
            if best_is_sco:
                job_sco_idx[j] += 1
            else:
                job_sfos[j].remove(best_candidate)

            # Ghi nhận lịch trình
            schedule.append({
                'job_id': j,
                'op_id': op_id,
                'type': 'SCO' if best_is_sco else 'SFO',
                'machine': best_machine,
                'start_time': best_start_time,
                'end_time': best_finish_time,
                'proc_time': best_proc_time
            })

            scheduled_count += 1
        else:
            break

    makespan = max(job_free_time.values()) if job_free_time else 0

    print(f"=== GREEDY INITIAL SOLUTION ===")
    print(f"Scheduled Operations: {scheduled_count}/{total_ops}")
    print(f"Makespan (UB): {makespan}")
    return makespan, schedule


def pre_processing(num_jobs, SCO, SFO, ub):
    
    feasible_time = {}
    min_proc_time = {}

    # 1. Tính thời gian gia công nhỏ nhất p_min của từng thao tác
    for op in SCO + SFO:
        key = (op['job_id'], op['op_id'])
        min_proc_time[key] = min(op['request_list'].values())

    # 2. Gom nhóm SCO theo từng Job và sắp xếp theo op_id
    job_scos = defaultdict(list)
    for op in SCO:
        job_scos[op['job_id']].append(op)

    for j in job_scos:
        job_scos[j].sort(key=lambda x: x['op_id'])

    # 3. Tính EST và LST cho các thao tác SCO (Forward Pass & Backward Pass)
    for j in range(num_jobs):
        scos = job_scos[j]

        if scos:
            # Forward pass: Tính EST cho chuỗi SCO
            curr_est = 0
            for op in scos:
                key = (j, op['op_id'])
                feasible_time[key] = [curr_est, None]
                curr_est += min_proc_time[key]

            # Backward pass: Tính LST cho chuỗi SCO từ Upper Bound
            curr_lst = ub
            for op in reversed(scos):
                key = (j, op['op_id'])
                lst = curr_lst - min_proc_time[key]
                feasible_time[key][1] = lst
                curr_lst = lst

    # 4. Tính EST và LST cho các thao tác SFO
    for op in SFO:
        key = (op['job_id'], op['op_id'])
        est = 0
        lst = ub - min_proc_time[key]
        feasible_time[key] = [est, lst]

    # 5. Kiểm tra tính hợp lệ của miền thời gian
    is_feasible = True
    result_feasible_time = {}

    for key, (est, lst) in feasible_time.items():
        if est > lst:
            print(f"Job {key[0]} - Op {key[1]} can't schedule: EST ({est}) > LST ({lst})")
            is_feasible = False
        result_feasible_time[key] = (est, lst)

    return result_feasible_time, is_feasible


def create_var(SCO, SFO, feasible_time):
    
    s = {}
    x = {}
    m = {}
    xm = {}
    y = {}
    counter = 0

    all_ops = SCO + SFO
    sfo_keys = {(op['job_id'], op['op_id']) for op in SFO}

    for op in all_ops:
        key = (op['job_id'], op['op_id'])
        est, lst = feasible_time[key]

        # 1. Khởi tạo các biến thời gian (s và x) trong khoảng [EST, LST]
        for t in range(est, lst + 1):
            counter += 1
            s[(key, t)] = counter
            counter += 1
            x[(key, t)] = counter

        # 2. Khởi tạo các biến chọn máy (m và xm) cho các máy khả thi
        for machine in op['request_list'].keys():
            counter += 1
            m[(key, machine)] = counter
            counter += 1
            xm[(key, machine)] = counter

    # 3. Khởi tạo biến thứ tự y cho các cặp nguyên công trong CÙNG MỘT CÔNG VIỆC (i < j, ít nhất một SFO)
    job_ops = defaultdict(list)
    for op in all_ops:
        job_ops[op['job_id']].append(op)

    for j_id, ops in job_ops.items():
        ops.sort(key=lambda o: o['op_id'])
        num_ops = len(ops)
        for a in range(num_ops):
            op_i = ops[a]
            key_i = (j_id, op_i['op_id'])
            for b in range(a + 1, num_ops):
                op_j = ops[b]
                key_j = (j_id, op_j['op_id'])
                # Chỉ định nghĩa biến y_{i,j} nếu ít nhất một nguyên công thuộc SFO
                if key_i in sfo_keys or key_j in sfo_keys:
                    counter += 1
                    y[(key_i, key_j)] = counter

    return s, x, m, xm, y, counter


def build_constraints(solver, SCO, SFO, feasible_time, s, x, m, xm, y, top_id, args):
    
    all_ops = SCO + SFO
    sfo_keys = {(op['job_id'], op['op_id']) for op in SFO}

    # Phân loại thao tác theo Job
    job_scos = defaultdict(list)
    for op in SCO:
        job_scos[op['job_id']].append(op)
    for j in job_scos:
        job_scos[j].sort(key=lambda o: o['op_id'])

    # -------------------------------------------------------------------------
    # 1. RÀNG BUỘC CƠ CẤU THỜI GIAN (x(t) <==> Start >= t)
    # -------------------------------------------------------------------------
    for op in all_ops:
        key = (op['job_id'], op['op_id'])
        est, lst = feasible_time[key]

        # ĐIỀU KIỆN BIÊN: Luôn bắt đầu >= EST -> x(est) bắt buộc phải là True
        solver.add_clause([x[(key, est)]])

        for t in range(est, lst):
            # Tính đơn điệu: x(t+1) ==> x(t)
            solver.add_clause([-x[(key, t + 1)], x[(key, t)]])

            # Ràng buộc liên kết: s(t) <==> (x(t) AND NOT x(t+1))
            solver.add_clause([-s[(key, t)], x[(key, t)]])
            solver.add_clause([-s[(key, t)], -x[(key, t + 1)]])
            solver.add_clause([-x[(key, t)], x[(key, t + 1)], s[(key, t)]])

        # Tại thời điểm t = lst: s(lst) <==> x(lst)
        solver.add_clause([-s[(key, lst)], x[(key, lst)]])
        solver.add_clause([s[(key, lst)], -x[(key, lst)]])

    # -------------------------------------------------------------------------
    # 2. RÀNG BUỘC CHỌN ĐÚNG 1 MÁY (Sắp xếp theo thời gian xử lý tăng dần)
    # -------------------------------------------------------------------------
    for op in all_ops:
        key = (op['job_id'], op['op_id'])

        req_machines = sorted(
            op['request_list'].keys(),
            key=lambda machine_id: (op['request_list'][machine_id], machine_id)
        )

        solver.add_clause([xm[(key, req_machines[0])]])

        for idx in range(len(req_machines) - 1):
            curr_m = req_machines[idx]
            next_m = req_machines[idx + 1]

            solver.add_clause([-xm[(key, next_m)], xm[(key, curr_m)]])
            
            solver.add_clause([-m[(key, curr_m)], xm[(key, curr_m)]])
            solver.add_clause([-m[(key, curr_m)], -xm[(key, next_m)]])
            solver.add_clause([xm[(key, next_m)], -xm[(key, curr_m)], m[(key, curr_m)]])

        last_m = req_machines[-1]
        solver.add_clause([-m[(key, last_m)], xm[(key, last_m)]])
        solver.add_clause([-xm[(key, last_m)], m[(key, last_m)]])

    # -------------------------------------------------------------------------
    # 3. RÀNG BUỘC THỨ TỰ THAO TÁC SCO (SCO Precedence: u -> v)
    # -------------------------------------------------------------------------
    for j, scos in job_scos.items():
        for k in range(len(scos) - 1):
            op_u = scos[k]
            op_v = scos[k + 1]
            key_u = (j, op_u['op_id'])
            key_v = (j, op_v['op_id'])

            est_u, lst_u = feasible_time[key_u]
            est_v, lst_v = feasible_time[key_v]

            for t_u in range(est_u, lst_u + 1):
                for machine_u, p_u in op_u['request_list'].items():
                    finish_u = t_u + p_u

                    if finish_u > lst_v:
                        solver.add_clause([-s[(key_u, t_u)], -m[(key_u, machine_u)]])
                    elif finish_u > est_v:
                        solver.add_clause([-s[(key_u, t_u)], -m[(key_u, machine_u)], x[(key_v, finish_u)]])

    # FULL_TRANSITIVE = True : Áp dụng cho tất cả u_idx -> v_idx (v_idx >= u_idx + 2)
    # FULL_TRANSITIVE = False: Chỉ áp dụng từ thao tác đầu tiên u_idx = 0 -> v_idx (v_idx >= 2)
    if args.full_transitive:
        FULL_TRANSITIVE = True
    else:
        FULL_TRANSITIVE = False

    for j, scos in job_scos.items():
        num_scos = len(scos)
        
        for u_idx in range(num_scos):
            # Nếu không bật FULL_TRANSITIVE, chỉ xét u_idx = 0 (thao tác đầu tiên)
            if not FULL_TRANSITIVE and u_idx > 0:
                break

            # Bắt đầu v_idx từ u_idx + 2 để loại bỏ các cặp liền kề (u_idx -> u_idx + 1)
            for v_idx in range(u_idx + 2, num_scos):
                op_u = scos[u_idx]
                op_v = scos[v_idx]
                key_u = (j, op_u['op_id'])
                key_v = (j, op_v['op_id'])

                est_u, lst_u = feasible_time[key_u]
                est_v, lst_v = feasible_time[key_v]

                # Thời gian gia công nhỏ nhất của u (độc lập với biến m)
                p_u_min = min(op_u['request_list'].values())

                # Tổng p_min của tất cả các thao tác trung gian nằm giữa u và v
                min_intermediate_time = sum(
                    min(scos[w]['request_list'].values())
                    for w in range(u_idx + 1, v_idx)
                )

                min_delay = p_u_min + min_intermediate_time

                for t_u in range(est_u, lst_u + 1):
                    earliest_start_v = t_u + min_delay

                    if earliest_start_v > lst_v:
                        solver.add_clause([-s[(key_u, t_u)]])
                    elif earliest_start_v > est_v:
                        solver.add_clause([
                            -s[(key_u, t_u)], 
                            x[(key_v, earliest_start_v)]
                        ])

    # -------------------------------------------------------------------------
    # 4. RÀNG BUỘC KHÔNG CHỒNG LẤP TRÊN MÁY (Machine-level Non-overlap)
    # -------------------------------------------------------------------------
    num_total_ops = len(all_ops)
    for i in range(num_total_ops):
        op_i = all_ops[i]
        key_i = (op_i['job_id'], op_i['op_id'])
        est_i, lst_i = feasible_time[key_i]

        for j in range(i + 1, num_total_ops):
            op_j = all_ops[j]
            key_j = (op_j['job_id'], op_j['op_id'])
            est_j, lst_j = feasible_time[key_j]

            common_machines = set(op_i['request_list'].keys()).intersection(set(op_j['request_list'].keys()))

            for m_common in common_machines:
                p_i = op_i['request_list'][m_common]
                p_j = op_j['request_list'][m_common]

                top_id += 1
                same_machine_var = top_id
                solver.add_clause([-m[(key_i, m_common)], -m[(key_j, m_common)], same_machine_var])
                if args.sm_mode == '2d':
                    solver.add_clause([-same_machine_var, m[(key_i, m_common)]])
                    solver.add_clause([-same_machine_var, m[(key_j, m_common)]])
                for t_i in range(est_i, lst_i + 1):
                    clause = [-same_machine_var, -s[(key_i, t_i)]]

                    start_after = t_i + p_i
                    if start_after <= est_j:
                        continue
                    elif start_after <= lst_j:
                        clause.append(x[(key_j, start_after)])

                    finish_before_idx = t_i - p_j + 1
                    if finish_before_idx > lst_j:
                        continue
                    elif finish_before_idx > est_j:
                        clause.append(-x[(key_j, finish_before_idx)])

                    solver.add_clause(clause)

    # -------------------------------------------------------------------------
    # 5. RÀNG BUỘC KHÔNG CHỒNG LẤP TRÊN CÙNG MỘT CÔNG VIỆC (Job-level Non-overlap)
    # -------------------------------------------------------------------------
    job_ops_map = defaultdict(list)
    for op in all_ops:
        job_ops_map[op['job_id']].append(op)

    for j_id, ops in job_ops_map.items():
        ops.sort(key=lambda o: o['op_id'])
        num_ops = len(ops)

        # 5a. Ràng buộc thời gian chạy không chồng lấn giữa hai nguyên công i < j
        for a in range(num_ops):
            op_i = ops[a]
            key_i = (j_id, op_i['op_id'])
            est_i, lst_i = feasible_time[key_i]

            for b in range(a + 1, num_ops):
                op_j = ops[b]
                key_j = (j_id, op_j['op_id'])
                est_j, lst_j = feasible_time[key_j]

                # Nếu cả 2 đều là SCO, thứ tự i -> j đã cố định, bỏ qua biến y
                if key_i not in sfo_keys and key_j not in sfo_keys:
                    continue

                y_var = y[(key_i, key_j)]

                # TH1: Nếu i trước j (y_{i,j} = 1):
                # \neg y_{i,j} \vee \neg m_{i,k} \vee \neg s_{i,t} \vee x_{j, t + p_{i,k}}
                for k, p_ik in op_i['request_list'].items():
                    for t in range(est_i, lst_i + 1):
                        clause = [-y_var, -m[(key_i, k)], -s[(key_i, t)]]
                        start_after = t + p_ik
                        if start_after <= est_j:
                            continue  # Tautology (x_{j, start_after} luôn đúng)
                        elif start_after <= lst_j:
                            clause.append(x[(key_j, start_after)])
                        solver.add_clause(clause)

                # TH2: Nếu j trước i (y_{i,j} = 0):
                # y_{i,j} \vee \neg m_{j,k} \vee \neg s_{j,t} \vee x_{i, t + p_{j,k}}
                for k, p_jk in op_j['request_list'].items():
                    for t in range(est_j, lst_j + 1):
                        clause = [y_var, -m[(key_j, k)], -s[(key_j, t)]]
                        start_after = t + p_jk
                        if start_after <= est_i:
                            continue  # Tautology (x_{i, start_after} luôn đúng)
                        elif start_after <= lst_i:
                            clause.append(x[(key_i, start_after)])
                        solver.add_clause(clause)

        # 5b. Ràng buộc bắc cầu chống chu trình cho biến y
        def get_y_val(op_u, op_v):
            key_u = (j_id, op_u['op_id'])
            key_v = (j_id, op_v['op_id'])
            if key_u not in sfo_keys and key_v not in sfo_keys:
                return True  # Cả 2 đều SCO, u < v nên y_{u,v} = 1 (True)
            return y[(key_u, key_v)]

        def add_transitive_clause(literals):
            clause = []
            for var, pol in literals:
                if var is True:
                    if pol == 1:
                        return  # Tautology, không cần thêm clause
                    # Nếu pol == -1, literal nhận giá trị False nên bỏ qua
                else:
                    clause.append(var * pol)
            solver.add_clause(clause)
        if args.order_transitive:
            for a in range(num_ops):
                for b in range(a + 1, num_ops):
                    for c_idx in range(b + 1, num_ops):
                        op_i = ops[a]
                        op_j = ops[b]
                        op_l = ops[c_idx]

                        y_ij = get_y_val(op_i, op_j)
                        y_jl = get_y_val(op_j, op_l)
                        y_il = get_y_val(op_i, op_l)

                        # \neg y_{i,j} \vee \neg y_{j,l} \vee y_{i,l}
                        add_transitive_clause([(y_ij, -1), (y_jl, -1), (y_il, 1)])

                        # y_{i,j} \vee y_{j,l} \vee \neg y_{i,l}
                        add_transitive_clause([(y_ij, 1), (y_jl, 1), (y_il, -1)])

    if args.symmetry:
        # Symmetry breaking constraints (Ít nhất 1 thao tác bắt đầu tại thời điểm t = 0)
        job_scos = defaultdict(list)
        job_sfos = defaultdict(list)
        
        for op in SCO:
            job_scos[op['job_id']].append(op)
        for op in SFO:
            job_sfos[op['job_id']].append(op)

        all_job_ids = set([op['job_id'] for op in SCO + SFO])
        candidate_first_ops = []

        for job_id in all_job_ids:
            # Thao tác SCO đầu tiên trong chuỗi của Job (nếu có)
            if job_scos[job_id]:
                first_sco = min(job_scos[job_id], key=lambda o: o['op_id'])
                candidate_first_ops.append(first_sco)

            # Tất cả thao tác SFO của Job (vì bất kỳ SFO nào cũng có thể chạy đầu tiên)
            candidate_first_ops.extend(job_sfos[job_id])

        # Tạo clause: Ít nhất 1 thao tác trong candidate_first_ops bắt đầu tại t = 0 (dùng biến s)
        first_start_clause = []
        for op in candidate_first_ops:
            op_key = (op['job_id'], op['op_id'])
            # Kiểm tra nếu t = 0 có tồn tại trong tập biến s (tương ứng EST = 0)
            if (op_key, 0) in s:
                first_start_clause.append(s[(op_key, 0)])

        if first_start_clause:
            solver.add_clause(first_start_clause)


def add_incremental_constraints(solver, SCO, SFO, feasible_time, ub, x, m):
    
    job_scos = defaultdict(list)
    job_sfos = defaultdict(list)

    for op in SCO:
        job_scos[op['job_id']].append(op)
    for op in SFO:
        job_sfos[op['job_id']].append(op)

    all_job_ids = set([op['job_id'] for op in SCO + SFO])
    candidate_last_ops = []

    for job_id in all_job_ids:
        if job_scos[job_id]:
            last_sco = max(job_scos[job_id], key=lambda o: o['op_id'])
            candidate_last_ops.append(last_sco)

        candidate_last_ops.extend(job_sfos[job_id])

    for op in candidate_last_ops:
        key = (op['job_id'], op['op_id'])
        est, lst = feasible_time[key]

        for machine, process_time in op['request_list'].items():
            limit_start_time = ub - process_time

            if limit_start_time < est:
                solver.add_clause([-m[(key, machine)]])
            elif limit_start_time < lst:
                solver.add_clause([-m[(key, machine)], -x[(key, limit_start_time + 1)]])


def solve_and_print(solver, SCO, SFO, s, m):
    if solver.solve():
        model = set(solver.get_model())

        machine_assignment = {}
        start_times = {}

        all_ops = SCO + SFO

        for op in all_ops:
            key = (op['job_id'], op['op_id'])
            for machine in op['request_list'].keys():
                if m[(key, machine)] in model:
                    machine_assignment[key] = machine
                    break

        for op in all_ops:
            key = (op['job_id'], op['op_id'])
            for (k, t), var_id in s.items():
                if k == key and var_id in model:
                    start_times[key] = t
                    break

        makespan = 0
        for op in all_ops:
            key = (op['job_id'], op['op_id'])
            assigned_m = machine_assignment[key]
            p_time = op['request_list'][assigned_m]
            finish_t = start_times[key] + p_time
            if finish_t > makespan:
                makespan = finish_t

        print(f"[SAT Found] Makespan = {makespan}")
        return machine_assignment, start_times, makespan
    else:
        print("[UNSAT] Can't find a better solution. OPTIMAL!")
        return None, None, None


def verify_schedule(num_jobs, num_machines, SCO, SFO, machine_assignment, start_times, expected_makespan=None):
    
    all_ops = SCO + SFO

    # Check varify machine assignment and start times
    for op in all_ops:
        key = (op['job_id'], op['op_id'])

        if key not in machine_assignment:
            print(f"[FAULT VERIFY] Operation Job {op['job_id']} - Op {op['op_id']} is not assigned to a machine!")
            return False

        assigned_m = machine_assignment[key]
        if assigned_m not in op['request_list']:
            print(f"[FAULT VERIFY] Operation Job {op['job_id']} - Op {op['op_id']} is assigned to machine {assigned_m} which is not in the allowed list!")
            return False

        if key not in start_times:
            print(f"[FAULT VERIFY] Operation Job {op['job_id']} - Op {op['op_id']} has no start time!")
            return False

        if start_times[key] < 0:
            print(f"[FAULT VERIFY] Operation Job {op['job_id']} - Op {op['op_id']} has a negative start time ({start_times[key]})!")
            return False

    # -------------------------------------------------------------------------
    # 2. KIỂM TRA CHỒNG LẤP TRÊN CÙNG MÁY (Machine-level Non-overlap)
    # -------------------------------------------------------------------------
    machine_usage = defaultdict(list)
    for op in all_ops:
        key = (op['job_id'], op['op_id'])
        m = machine_assignment[key]
        st = start_times[key]
        pt = op['request_list'][m]
        et = st + pt
        machine_usage[m].append((st, et, key))

    for m, intervals in machine_usage.items():
        # Sắp xếp các ca gia công trên máy theo thời gian bắt đầu
        intervals.sort(key=lambda x: x[0])
        for i in range(len(intervals) - 1):
            st1, et1, key1 = intervals[i]
            st2, et2, key2 = intervals[i + 1]
            if et1 > st2:
                print(f"[FAULT VERIFY] Overlap per machine {m}: Operation {key1} [{st1}->{et1}] over Operation {key2} [{st2}->{et2}]")
                return False

    # -------------------------------------------------------------------------
    # 3. KIỂM TRA CHỒNG LẤP TRÊN CÙNG JOB (Job-level Non-overlap)
    # -------------------------------------------------------------------------
    job_usage = defaultdict(list)
    for op in all_ops:
        key = (op['job_id'], op['op_id'])
        st = start_times[key]
        m = machine_assignment[key]
        pt = op['request_list'][m]
        et = st + pt
        job_usage[op['job_id']].append((st, et, key))

    for j_id, intervals in job_usage.items():
        # Sắp xếp các ca gia công của Job theo thời gian bắt đầu
        intervals.sort(key=lambda x: x[0])
        for i in range(len(intervals) - 1):
            st1, et1, key1 = intervals[i]
            st2, et2, key2 = intervals[i + 1]
            if et1 > st2:
                print(f"[FAULT VERIFY] Overlap per job {j_id}: Operation {key1} [{st1}->{et1}] over Operation {key2} [{st2}->{et2}]")
                return False

    # -------------------------------------------------------------------------
    # 4. KIỂM TRA THỨ TỰ CÁC THAO TÁC SCO (SCO Precedence Constraints)
    # -------------------------------------------------------------------------
    job_scos = defaultdict(list)
    for op in SCO:
        job_scos[op['job_id']].append(op)

    for j_id, scos in job_scos.items():
        scos.sort(key=lambda o: o['op_id'])
        for i in range(len(scos) - 1):
            op_u = scos[i]
            op_v = scos[i + 1]
            key_u = (j_id, op_u['op_id'])
            key_v = (j_id, op_v['op_id'])

            m_u = machine_assignment[key_u]
            et_u = start_times[key_u] + op_u['request_list'][m_u]
            st_v = start_times[key_v]

            if et_u > st_v:
                print(f"[FAULT VERIFY] Violate sequence SCO at Job {j_id}: Op {op_u['op_id']} (end {et_u}) > Op {op_v['op_id']} (start {st_v})")
                return False

    # -------------------------------------------------------------------------
    # 5. KHỞI TẠO VÀ XÁC NHẬN MAKESPAN TỔNG
    # -------------------------------------------------------------------------
    calculated_makespan = max(
        start_times[(op['job_id'], op['op_id'])] + op['request_list'][machine_assignment[(op['job_id'], op['op_id'])]]
        for op in all_ops
    )

    if expected_makespan is not None and calculated_makespan != expected_makespan:
        print(f"[FAULT VERIFY] Makespan recompute ({calculated_makespan}) don't match ({expected_makespan})")
        return False

    print(f"[VERIFY] VERIFY SUCCESS]")
    return True


def main():
    parser = argparse.ArgumentParser(description="FJSDSP SAT Solver Configuration")
    
    parser.add_argument("file_path", nargs="?", default="Datasets/MPSFs/MPSF08.txt", help="Path to input dataset file")
    parser.add_argument("--symmetry", action=argparse.BooleanOptionalAction, default=False, help="Enable/Disable Symmetry Breaking constraint (default: False)")
    parser.add_argument("--sm-mode", choices=["1d", "2d"], default="2d", help="Same Machine selection mode: '1d'  or '2d'  (default: 2d)")
    parser.add_argument("--order_transitive", action=argparse.BooleanOptionalAction, default=False, help="Enable/Disable Order Transitive precedence constraints for Overlap Operations per Job ALL operations (SCO + SFO) (default: False)")
    parser.add_argument("--full-transitive", action=argparse.BooleanOptionalAction, default=False, help="Transitive mode: True for all pairs/triplets, False for first op only (default: False)")

    args = parser.parse_args()

    print("=== CONFIGURATION ===")
    print(f"File Path: {args.file_path}")
    print(f"Symmetry Breaking: {args.symmetry}")
    print(f"Same Machine Mode (sm_mode): {args.sm_mode}")
    print(f"Transitive Order Precedence (All Ops): {args.order_transitive}")
    print(f"Full Transitive: {args.full_transitive}")
    print("=====================\n")

    start_time = perf_counter()

    #Read data
    num_jobs, num_machines, SCO, SFO = read_file(args.file_path)
    if SCO is None:
        print("Failed to read SCO data. Exiting.")
        return

    # Greedy initial solution to get an upper bound
    greedy_ub, _ = greedy_schedule(num_jobs, num_machines, SCO, SFO)

    # Pre-processing to compute feasible time windows for all operations
    ub = greedy_ub - 1
    feasible_time, is_feasible = pre_processing(num_jobs, SCO, SFO, ub)
    if not is_feasible:
        print("Can not find feasible time windows for all operations. Exiting.")
        return

    # Initialize variables for PySAT
    s, x, m, xm, y, top_id = create_var(SCO, SFO, feasible_time)

    # Initialize PySAT solver and build constraints
    solver = Solver(name='cadical195')
    build_constraints(solver, SCO, SFO, feasible_time, s, x, m, xm, y, top_id, args)

    best_makespan = greedy_ub
    best_assignment = None
    best_start_times = None

    # Incremental solving loop to tighten the upper bound
    while True:
        print('-------------------------------------------------')
        # Add incremental constraints to enforce the current upper bound
        add_incremental_constraints(solver, SCO, SFO, feasible_time, ub, x, m)

        # Solve
        assignment, start_times, current_makespan = solve_and_print(solver, SCO, SFO, s, m)

        if current_makespan is not None:
            best_makespan = current_makespan
            best_assignment = assignment
            best_start_times = start_times

            # Tighten the upper bound for the next iteration
            ub = current_makespan - 1
        else:
            # No better solution found, exit the loop
            break
        if best_assignment is not None:
            # Verify the solution to ensure it meets all constraints
            is_valid = verify_schedule(
                num_jobs, 
                num_machines, 
                SCO, 
                SFO, 
                best_assignment, 
                best_start_times, 
                expected_makespan=best_makespan
            )
            
            if not is_valid:
                print("Warning: The best solution found is invalid. Please check the constraints and solver implementation.")
        print(f"Total Execution Time so far: {perf_counter() - start_time:.2f} seconds")

    total_execution_time = perf_counter() - start_time
    print("\n==========================================")
    print(f"OPTIMAL MAKESPAN: {best_makespan}")
    print(f"Total Execution Time: {total_execution_time:.2f} seconds")
    print("==========================================")


if __name__ == "__main__":
    main()
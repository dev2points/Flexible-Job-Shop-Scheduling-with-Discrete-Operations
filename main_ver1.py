from collections import defaultdict
import re
import sys
from time import perf_counter
from pysat.solvers import Solver


def read_file(file_path):
    print(f"Reading data from: {file_path}")
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
            if "PSF" in file_path.upper():
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
        print(f"Error: File not found at path '{file_path}'")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

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
    print("================================")

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
            print(f" Job {key[0]} - Op {key[1]} Can't schedule: EST ({est}) > LST ({lst})")
            is_feasible = False
        result_feasible_time[key] = (est, lst)

    return result_feasible_time, is_feasible


def create_var(SCO, SFO, feasible_time):
    """
    Tạo và ánh xạ các biến Boolean cho mô hình PySAT.

    Args:
        SCO (list): Danh sách các thao tác SCO.
        SFO (list): Danh sách các thao tác SFO.
        feasible_time (dict): Miền thời gian khả thi (EST, LST) dạng {(job_id, op_id): (est, lst)}.

    Returns:
        s (dict): Ánh xạ biến thời gian chính xác s[((job_id, op_id), t)] -> ID biến SAT.
        x (dict): Ánh xạ biến thang thời gian x[((job_id, op_id), t)] -> ID biến SAT.
        m (dict): Ánh xạ biến chọn máy m[((job_id, op_id), machine_id)] -> ID biến SAT.
        xm (dict): Ánh xạ biến thang chọn máy xm[((job_id, op_id), machine_id)] -> ID biến SAT.
        counter (int): Tổng số biến SAT đã tạo (dùng làm ID bắt đầu cho các biến phụ sinh ra sau này).
    """
    s = {}
    x = {}
    m = {}
    xm = {}
    counter = 0

    # Gom toàn bộ thao tác SCO và SFO
    all_ops = SCO + SFO

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

    return s, x, m, xm, counter

def build_constraints(solver, SCO, SFO, feasible_time, s, x, m, xm):
   
    all_ops = SCO + SFO

    # Phân loại thao tác theo Job
    job_scos = defaultdict(list)
    for op in SCO:
        job_scos[op['job_id']].append(op)
    for j in job_scos:
        job_scos[j].sort(key=lambda o: o['op_id'])

    # Link between s and x variables (Linking s and x)
    for op in all_ops:
        key = (op['job_id'], op['op_id'])
        est, lst = feasible_time[key]

        # ĐIỀU KIỆN BIÊN: Luôn bắt đầu >= EST -> x(est) bắt buộc phải là True
        solver.add_clause([x[(key, est)]])

        for t in range(est, lst):
            # Tính đơn điệu: x(t+1) ==> x(t)  (Nếu >= t+1 thì chắc chắn >= t)
            solver.add_clause([-x[(key, t + 1)], x[(key, t)]])

            # Ràng buộc liên kết: s(t) <==> (x(t) AND NOT x(t+1))
            solver.add_clause([-s[(key, t)], x[(key, t)]])
            solver.add_clause([-s[(key, t)], -x[(key, t + 1)]])
            solver.add_clause([-x[(key, t)], x[(key, t + 1)], s[(key, t)]])

        # Tại thời điểm t = lst: s(lst) <==> x(lst)
        solver.add_clause([-s[(key, lst)], x[(key, lst)]])
        solver.add_clause([s[(key, lst)], -x[(key, lst)]])

    # Link between m and xm variables (Linking m and xm)
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

    # Precedence constraints for SCO operations (SCO Precedence Constraints)
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
                    finish_u = t_u + p_u  # Thời điểm tối thiểu v phải bắt đầu (start_v >= finish_u)

                    if finish_u > lst_v:
                        # Vượt quá LST của v -> Không thể bắt đầu u tại t_u trên máy machine_u
                        solver.add_clause([-s[(key_u, t_u)], -m[(key_u, machine_u)]])
                    elif finish_u > est_v:
                        # start_v >= finish_u  <==>  x_v(finish_u) = True
                        solver.add_clause([-s[(key_u, t_u)], -m[(key_u, machine_u)], x[(key_v, finish_u)]])

    # Non-overlap constraints for operations on the same machine (Machine-level Non-overlap)
    num_total_ops = len(all_ops)
    top_id = solver.nof_vars() + 1  # ID biến mới bắt đầu từ đây
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

                top_id += 1  # Biến phụ mới cho ràng buộc không chồng lấp trên máy m_common
                same_machine_var = top_id
                solver.add_clause([-m[(key_i, m_common)], -m[(key_j, m_common)], same_machine_var])
                solver.add_clause([-same_machine_var, m[(key_i, m_common)]])
                solver.add_clause([-same_machine_var, m[(key_j, m_common)]])
                for t_i in range(est_i, lst_i + 1):
                    clause = [-same_machine_var, -s[(key_i, t_i)]]
                # for t_i in range(est_i, lst_i + 1):
                #     clause = [-m[(key_i, m_common)], -m[(key_j, m_common)], -s[(key_i, t_i)]]

                    # TH1: Thao tác j chạy SAU thao tác i (start_j >= t_i + p_i)
                    start_after = t_i + p_i
                    if start_after <= est_j:
                        continue  # Luôn đúng (Tautology)
                    elif start_after <= lst_j:
                        clause.append(x[(key_j, start_after)])

                    # TH2: Thao tác j chạy TRƯỚC thao tác i (start_j <= t_i - p_j)
                    # start_j <= t_i - p_j  <==>  NOT (start_j >= t_i - p_j + 1)  <==>  -x_j(t_i - p_j + 1)
                    finish_before_idx = t_i - p_j + 1
                    if finish_before_idx > lst_j:
                        continue  # Luôn đúng (Tautology)
                    elif finish_before_idx > est_j:
                        clause.append(-x[(key_j, finish_before_idx)])

                    solver.add_clause(clause)

    # Non-overlap constraints for operations of the same job (Job-level Non-overlap)
    for i in range(num_total_ops):
        op_i = all_ops[i]
        key_i = (op_i['job_id'], op_i['op_id'])
        est_i, lst_i = feasible_time[key_i]

        for j in range(i + 1, num_total_ops):
            op_j = all_ops[j]
            key_j = (op_j['job_id'], op_j['op_id'])
            est_j, lst_j = feasible_time[key_j]

            if op_i['job_id'] == op_j['job_id']:
                is_i_sco = any(op_i['op_id'] == o['op_id'] for o in job_scos[op_i['job_id']])
                is_j_sco = any(op_j['op_id'] == o['op_id'] for o in job_scos[op_j['job_id']])
                if is_i_sco and is_j_sco:
                    continue

                for m_i, p_i in op_i['request_list'].items():
                    for m_j, p_j in op_j['request_list'].items():
                        if m_i == m_j:
                            continue

                        for t_i in range(est_i, lst_i + 1):
                            clause = [-m[(key_i, m_i)], -m[(key_j, m_j)], -s[(key_i, t_i)]]

                            # TH1: j chạy sau i (start_j >= t_i + p_i)
                            start_after = t_i + p_i
                            if start_after <= est_j:
                                continue
                            elif start_after <= lst_j:
                                clause.append(x[(key_j, start_after)])

                            # TH2: j chạy trước i (start_j <= t_i - p_j)
                            finish_before_idx = t_i - p_j + 1
                            if finish_before_idx > lst_j:
                                continue
                            elif finish_before_idx > est_j:
                                clause.append(-x[(key_j, finish_before_idx)])

                            solver.add_clause(clause)

        

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
    
    # 1. Xác định các thao tác có thể là thao tác kết thúc (Last Operations) của mỗi Job
    job_scos = defaultdict(list)
    job_sfos = defaultdict(list)

    for op in SCO:
        job_scos[op['job_id']].append(op)
    for op in SFO:
        job_sfos[op['job_id']].append(op)

    all_job_ids = set([op['job_id'] for op in SCO + SFO])
    candidate_last_ops = []

    for job_id in all_job_ids:
        # Thao tác SCO cuối cùng trong chuỗi của Job (nếu có)
        if job_scos[job_id]:
            last_sco = max(job_scos[job_id], key=lambda o: o['op_id'])
            candidate_last_ops.append(last_sco)

        # Tất cả thao tác SFO của Job (vì bất kỳ SFO nào cũng có thể chạy cuối cùng)
        candidate_last_ops.extend(job_sfos[job_id])

    # 2. Thêm ràng buộc ép thời gian hoàn thành <= UB
    for op in candidate_last_ops:
        key = (op['job_id'], op['op_id'])
        est, lst = feasible_time[key]

        for machine, process_time in op['request_list'].items():
            # Thời điểm bắt đầu trễ nhất cho phép trên máy này để không vượt UB
            limit_start_time = ub - process_time

            if limit_start_time < est:
                # Không thể chọn máy này nữa vì ngay cả khi bắt đầu tại EST vẫn bị lố UB
                solver.add_clause([-m[(key, machine)]])
            elif limit_start_time < lst:
                # 
                solver.add_clause([-m[(key, machine)], -x[(key, limit_start_time+1)]])

def solve_and_print(solver, SCO, SFO, s, m):
    if solver.solve():
        model = set(solver.get_model())

        machine_assignment = {}
        start_times = {}

        all_ops = SCO + SFO

        # Compute machine assignments
        for op in all_ops:
            key = (op['job_id'], op['op_id'])
            for machine in op['request_list'].keys():
                if m[(key, machine)] in model:
                    machine_assignment[key] = machine
                    break

        # Compute start times
        for op in all_ops:
            key = (op['job_id'], op['op_id'])
            for (k, t), var_id in s.items():
                if k == key and var_id in model:
                    start_times[key] = t
                    break

        # Compute makespan
        makespan = 0
        for op in all_ops:
            key = (op['job_id'], op['op_id'])
            assigned_m = machine_assignment[key]
            p_time = op['request_list'][assigned_m]
            finish_t = start_times[key] + p_time
            if finish_t > makespan:
                makespan = finish_t

        print(f"[SAT Found]  Makespan = {makespan}")
        return machine_assignment, start_times, makespan
    else:
        print("[UNSAT] No better solution found. OPTIMAL!")
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
                print(f"[LỖI VERIFY] Trùng máy {m}: Thao tác {key1} [{st1}->{et1}] đè lên thao tác {key2} [{st2}->{et2}]")
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
                print(f"[LỖI VERIFY] Trùng Job {j_id}: Thao tác {key1} [{st1}->{et1}] đè lên thao tác {key2} [{st2}->{et2}]")
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
                print(f"[LỖI VERIFY] Vi phạm thứ tự SCO ở Job {j_id}: Op {op_u['op_id']} (kết thúc {et_u}) > Op {op_v['op_id']} (bắt đầu {st_v})")
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

    print(f"[VERIFY SUCCESS]")
    return True



def main():
    file_path = sys.argv[1] if len(sys.argv) > 1 else "Datasets/MPSFs/MPSF08.txt"

    start_time = perf_counter()

    #Read data
    num_jobs, num_machines, SCO, SFO = read_file(file_path)
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
    s, x, m, xm, top_id = create_var(SCO, SFO, feasible_time)

    # Initialize PySAT solver and build constraints
    solver = Solver(name='cadical195')
    build_constraints(solver, SCO, SFO, feasible_time, s, x, m, xm)

    best_makespan = greedy_ub
    best_assignment = None
    best_start_times = None

    # Incremental solving loop to tighten the upper bound
    while True:
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
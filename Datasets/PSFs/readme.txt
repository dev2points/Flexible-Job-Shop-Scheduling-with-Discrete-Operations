Instances illustration
A necessary explaination for instances is given below. Taking the instance PSF01_10x7 as an example.

10 7
13 12 11 11 15 15 12
3 3 2 3 2 3 3
5 3 3 (2 19 4 18 6 24) 2 (3 57 6 76) 5 (2 63 3 91 4 87 5 99 6 99) 2 3 (1 55 3 52 7 61) 2 (3 32 4 34)
5 2 4 (2 16 4 16 6 21 7 18) 3 (2 48 6 58 7 56) 3 4 (1 17 2 16 4 16 6 16) 2 (1 29 5 32) 5 (1 81 3 69 4 68 5 64 7 86)
5 5 5 (3 42 4 34 5 30 6 36 7 32) 5 (2 105 3 99 4 111 5 114 7 88) 3 (1 41 4 50 5 36) 3 (4 26 5 31 6 30) 5 (1 13 2 13 3 10 4 15 6 8)
5 3 5 (1 51 2 77 3 88 5 70 6 81) 3 (4 47 5 60 7 57) 2 (3 83 6 70) 2 5 (1 66 2 59 3 73 5 72 7 76) 2 (1 96 6 78)
5 2 5 (1 80 3 81 5 71 6 91 7 79) 5 (2 27 3 31 5 39 6 37 7 33) 3 2 (1 58 5 72) 2 (5 23 7 20) 4 (1 26 5 44 6 35 7 40)
5 3 4 (2 61 4 51 5 72 6 38) 5 (1 43 2 41 3 49 4 40 5 34) 5 (2 79 3 66 4 78 5 91 7 71) 2 2 (6 76 7 85) 4 (3 63 4 65 6 47 7 65)
5 2 2 (1 70 6 68) 4 (1 71 2 67 3 62 6 71) 3 5 (1 87 2 92 3 65 5 73 6 84) 3 (1 71 3 73 6 60) 3 (2 97 5 84 7 87)
5 5 3 (2 31 6 42 7 37) 4 (1 62 4 43 6 68 7 71) 2 (4 37 5 36) 2 (1 28 7 19) 3 (1 95 6 72 7 73)
5 3 2 (2 15 4 16) 5 (3 48 4 32 5 46 6 48 7 59) 2 (1 29 6 24) 2 2 (2 47 3 49) 2 (1 111 3 108)
5 5 3 (1 76 4 89 5 63) 2 (3 80 6 114) 2 (5 45 7 37) 5 (1 78 3 69 4 62 5 62 6 75) 4 (1 90 2 91 4 86 5 73)


The first row '10 7' records the information of total number of jobs and total number of machines. From the left to right, 10 represents the total number of jobs;  7 represents the total number of machines.

The second row '13 12 11 11 15 15 12' records the information of  processing power of each machine from left to right.

The third row '3 3 2 3 2 3 3' records the information of  stand-by power of each machine from left to right.

The 4th row '5 3 3 (2 19 4 18 6 24) 2 (3 57 6 76) 5 (2 63 3 91 4 87 5 99 6 99) 2 3 (1 55 3 52 7 61) 2 (3 32 4 34)' records the information of  job 1. From the left to right, 5 represents the total operations of job 1; ...

'3' represents 3 sequence-constrained operations of job 1; '3' represents 3 machines that can process operation 1 of job 1(O11); '(2 19 4 18 6 24)' represents that machine 2, machine 4 and machine 6 can process O11, and the processing time are 19, 18 and 24, respectively; '2' represents 2 machines that can process operation 2 of job 1(O12); '(3 57 6 76)' represents that machine 3 and machine 6 can process O12, and the processing time are 57 and 76, respectively; '5' represents 5 machines that can process operation 3 of job 1(O13); '(2 63 3 91 4 87 5 99 6 99)' represents that machine 2, machine 3, machine 4, machine 5 and machine 6 can process O13, and the processing time are 63, 91, 87, 99 and 99, respectively; ...

 '2' presents 2 sequence-free operations of job 1; '3' represents 3 machines that can process operation a of job 1(O1a); '(1 55 3 52 7 61)' represents that machine 1, machine 3 and machine 7 can process O1a, and the processing time are 55, 52 and 61, respectively; '2' represents 2 machines that can process operation b of job 1(O1b); '(3 32 4 34)' represents that machine 3 and machine 4 can process O1b, and the processing time are 32 and 34, respectively; 

The 5th to 13th rows record the information of jobs 2 to 10. The information of them can be described like as job 1.




from cpu_scheduler import Process, run_simulation
import json

def test_all():
    # Sample processes
    # PID, Arrival, Burst, Priority
    data = [
        (1, 0, 8, 2),
        (2, 1, 4, 1),
        (3, 2, 9, 3),
        (4, 3, 5, 2)
    ]
    processes = [Process(d[0], d[1], d[2], d[3]) for d in data]
    
    algorithms = ['FCFS', 'SJF_NP', 'SRTF', 'PRIO_NP', 'PRIO_P', 'RR']
    results = {}
    
    for algo in algorithms:
        print(f"Testing {algo}...")
        if algo == 'RR':
            results[algo] = run_simulation(algo, processes, quantum=2)
        else:
            results[algo] = run_simulation(algo, processes)
            
    # Quick verification of FCFS
    # P1: Arrv 0, Burst 8 -> CT 8, TAT 8, WT 0
    # P2: Arrv 1, Burst 4 -> CT 12, TAT 11, WT 7
    # P3: Arrv 2, Burst 9 -> CT 21, TAT 19, WT 10
    # P4: Arrv 3, Burst 5 -> CT 26, TAT 23, WT 18
    # TAT Sum: 8 + 11 + 19 + 23 = 61. Avg: 61/4 = 15.25
    # WT Sum: 0 + 7 + 10 + 18 = 35. Avg: 35/4 = 8.75
    fcfs_res = results['FCFS']
    print(f"FCFS Avg TAT: {fcfs_res['avg_tat']}")
    assert fcfs_res['processes'][0]['completion_time'] == 8
    assert fcfs_res['avg_tat'] == 15.25
    
    print("All tests passed basic checks!")
    # Output one for inspection
    # print(json.dumps(results['SRTF'], indent=2))

if __name__ == "__main__":
    test_all()

import copy

class Process:
    def __init__(self, pid, arrival_time, burst_time, priority=0):
        self.pid = pid
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.priority = priority
        self.remaining_time = burst_time
        
        # Result fields
        self.completion_time = 0
        self.turnaround_time = 0
        self.waiting_time = 0

    def to_dict(self):
        return {
            "pid": self.pid,
            "arrival_time": self.arrival_time,
            "burst_time": self.burst_time,
            "priority": self.priority,
            "completion_time": self.completion_time,
            "turnaround_time": self.turnaround_time,
            "waiting_time": self.waiting_time
        }

class SchedulerResult:
    def __init__(self, processes, gantt_chart):
        self.processes = sorted(processes, key=lambda x: x.pid)
        self.gantt_chart = gantt_chart
        self.calculate_averages()

    def calculate_averages(self):
        total_tat = sum(p.turnaround_time for p in self.processes)
        total_wt = sum(p.waiting_time for p in self.processes)
        self.avg_tat = total_tat / len(self.processes) if self.processes else 0
        self.avg_wt = total_wt / len(self.processes) if self.processes else 0

    def get_summary(self):
        return {
            "processes": [p.to_dict() for p in self.processes],
            "gantt_chart": self.gantt_chart,
            "avg_tat": self.avg_tat,
            "avg_wt": self.avg_wt
        }

def calculate_metrics(p):
    """Utility to calculate TAT and WT once CT is set."""
    p.turnaround_time = p.completion_time - p.arrival_time
    p.waiting_time = p.turnaround_time - p.burst_time
    return p

def fcfs(processes):
    procs = sorted([copy.deepcopy(p) for p in processes], key=lambda x: (x.arrival_time, x.pid))
    gantt_chart = []
    current_time = 0
    
    for p in procs:
        if current_time < p.arrival_time:
            gantt_chart.append(("IDLE", current_time, p.arrival_time))
            current_time = p.arrival_time
        
        start_time = current_time
        current_time += p.burst_time
        p.completion_time = current_time
        calculate_metrics(p)
        gantt_chart.append((p.pid, start_time, current_time))
        
    return SchedulerResult(procs, gantt_chart)

def sjf_non_preemptive(processes):
    procs = [copy.deepcopy(p) for p in processes]
    completed = []
    gantt_chart = []
    current_time = 0
    
    while len(completed) < len(procs):
        # Filter processes that have arrived and are not yet completed
        available = [p for p in procs if p.arrival_time <= current_time and p not in completed]
        
        if not available:
            # Find the next arrival time
            next_arrival = min(p.arrival_time for p in procs if p not in completed)
            gantt_chart.append(("IDLE", current_time, next_arrival))
            current_time = next_arrival
            continue
        
        # Pick process with shortest burst time, tie-break with arrival time
        p = min(available, key=lambda x: (x.burst_time, x.arrival_time, x.pid))
        
        start_time = current_time
        current_time += p.burst_time
        p.completion_time = current_time
        calculate_metrics(p)
        gantt_chart.append((p.pid, start_time, current_time))
        completed.append(p)
        
    return SchedulerResult(completed, gantt_chart)

def srtf(processes):
    procs = [copy.deepcopy(p) for p in processes]
    n = len(procs)
    completed_count = 0
    current_time = 0
    gantt_chart = []
    last_pid = None
    start_time = 0
    
    while completed_count < n:
        available = [p for p in procs if p.arrival_time <= current_time and p.remaining_time > 0]
        
        if not available:
            if last_pid is not None:
                gantt_chart.append((last_pid, start_time, current_time))
                last_pid = None
            
            # Move to next arrival
            next_arrival = min(p.arrival_time for p in procs if p.remaining_time > 0)
            gantt_chart.append(("IDLE", current_time, next_arrival))
            current_time = next_arrival
            continue
            
        # Shortest Remaining Time First, tie-break with arrival time
        p = min(available, key=lambda x: (x.remaining_time, x.arrival_time, x.pid))
        
        if p.pid != last_pid:
            if last_pid is not None:
                gantt_chart.append((last_pid, start_time, current_time))
            last_pid = p.pid
            start_time = current_time
            
        p.remaining_time -= 1
        current_time += 1
        
        if p.remaining_time == 0:
            p.completion_time = current_time
            calculate_metrics(p)
            completed_count += 1
            gantt_chart.append((p.pid, start_time, current_time))
            last_pid = None
            
    return SchedulerResult(procs, gantt_chart)

def priority_non_preemptive(processes):
    procs = [copy.deepcopy(p) for p in processes]
    completed = []
    gantt_chart = []
    current_time = 0
    
    while len(completed) < len(procs):
        available = [p for p in procs if p.arrival_time <= current_time and p not in completed]
        
        if not available:
            next_arrival = min(p.arrival_time for p in procs if p not in completed)
            gantt_chart.append(("IDLE", current_time, next_arrival))
            current_time = next_arrival
            continue
        
        # Priority (lower number usually means higher priority), tie-break with arrival
        p = min(available, key=lambda x: (x.priority, x.arrival_time, x.pid))
        
        start_time = current_time
        current_time += p.burst_time
        p.completion_time = current_time
        calculate_metrics(p)
        gantt_chart.append((p.pid, start_time, current_time))
        completed.append(p)
        
    return SchedulerResult(completed, gantt_chart)

def priority_preemptive(processes):
    procs = [copy.deepcopy(p) for p in processes]
    n = len(procs)
    completed_count = 0
    current_time = 0
    gantt_chart = []
    last_pid = None
    start_time = 0
    
    while completed_count < n:
        available = [p for p in procs if p.arrival_time <= current_time and p.remaining_time > 0]
        
        if not available:
            if last_pid is not None:
                gantt_chart.append((last_pid, start_time, current_time))
                last_pid = None
            next_arrival = min(p.arrival_time for p in procs if p.remaining_time > 0)
            gantt_chart.append(("IDLE", current_time, next_arrival))
            current_time = next_arrival
            continue
            
        p = min(available, key=lambda x: (x.priority, x.arrival_time, x.pid))
        
        if p.pid != last_pid:
            if last_pid is not None:
                gantt_chart.append((last_pid, start_time, current_time))
            last_pid = p.pid
            start_time = current_time
            
        p.remaining_time -= 1
        current_time += 1
        
        if p.remaining_time == 0:
            p.completion_time = current_time
            calculate_metrics(p)
            completed_count += 1
            gantt_chart.append((p.pid, start_time, current_time))
            last_pid = None
            
    return SchedulerResult(procs, gantt_chart)

def round_robin(processes, quantum):
    procs = sorted([copy.deepcopy(p) for p in processes], key=lambda x: x.arrival_time)
    queue = []
    current_time = 0
    completed = []
    gantt_chart = []
    
    idx = 0
    while idx < len(procs) and procs[idx].arrival_time <= current_time:
        queue.append(procs[idx])
        idx += 1
        
    while queue or idx < len(procs):
        if not queue:
            gantt_chart.append(("IDLE", current_time, procs[idx].arrival_time))
            current_time = procs[idx].arrival_time
            while idx < len(procs) and procs[idx].arrival_time <= current_time:
                queue.append(procs[idx])
                idx += 1
        
        p = queue.pop(0)
        start_time = current_time
        exec_time = min(p.remaining_time, quantum)
        
        p.remaining_time -= exec_time
        current_time += exec_time
        gantt_chart.append((p.pid, start_time, current_time))
        
        # Check for new arrivals while process was running
        while idx < len(procs) and procs[idx].arrival_time <= current_time:
            queue.append(procs[idx])
            idx += 1
            
        if p.remaining_time > 0:
            queue.append(p)
        else:
            p.completion_time = current_time
            calculate_metrics(p)
            completed.append(p)
            
    return SchedulerResult(completed, gantt_chart)

def run_simulation(algorithm, processes, quantum=None):
    """
    Main entry point for running a simulation.
    algorithm: str ('FCFS', 'SJF_NP', 'SRTF', 'PRIO_NP', 'PRIO_P', 'RR')
    processes: list of Process objects
    quantum: int (required for RR)
    """
    if algorithm == 'FCFS':
        return fcfs(processes).get_summary()
    elif algorithm == 'SJF_NP':
        return sjf_non_preemptive(processes).get_summary()
    elif algorithm == 'SRTF':
        return srtf(processes).get_summary()
    elif algorithm == 'PRIO_NP':
        return priority_non_preemptive(processes).get_summary()
    elif algorithm == 'PRIO_P':
        return priority_preemptive(processes).get_summary()
    elif algorithm == 'RR':
        if quantum is None:
            raise ValueError("Quantum is required for Round Robin")
        return round_robin(processes, quantum).get_summary()
    else:
        raise ValueError(f"Unknown algorithm: {algorithm}")

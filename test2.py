import sys
from collections import deque

class Process:
    def __init__(self, pid, name, arrival_time, burst_time):
        self.pid = pid
        self.name = name
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.remaining_time = burst_time
        self.finish_time = 0
        self.waiting_time = 0
        self.turnaround_time = 0

def read_processes(filename):
    processes = []
    try:
        with open(filename, 'r') as file:
            for line in file:
                pid, name, arrival_time, burst_time = line.strip().split()
                processes.append(Process(
                    int(pid), 
                    name, 
                    int(arrival_time), 
                    int(burst_time)
                ))
    except FileNotFoundError:
        print(f"Error: File {filename} not found.")
        sys.exit(1)
    return processes

def consolidate_intervals(intervals):
    if not intervals:
        return []
        
    # Sort intervals by start time
    sorted_intervals = sorted(intervals, key=lambda x: x[1])
    
    consolidated = []
    current_process = sorted_intervals[0][0]
    current_start = sorted_intervals[0][1]
    current_end = sorted_intervals[0][2]
    
    for process, start, end in sorted_intervals[1:]:
        if process == current_process and start == current_end:
            # Extend the current interval
            current_end = end
        else:
            # Add the completed interval and start a new one
            consolidated.append((current_process, current_start, current_end))
            current_process = process
            current_start = start
            current_end = end
    
    # Add the last interval
    consolidated.append((current_process, current_start, current_end))
    
    return consolidated

def print_schedule_results(processes, algorithm_name, gantt_intervals):
    print(f"\n{algorithm_name} Scheduling Results:")
    print("Process  Finish-Time  Waiting-Time  Turnaround-Time")
    
    # Sort processes by pid for consistent output
    sorted_processes = sorted(processes, key=lambda x: x.pid)
    for p in sorted_processes:
        print(f"{p.name:<8} {p.finish_time:<12} {p.waiting_time:<13} {p.turnaround_time:<15}")
    
    print("\nGantt Chart:")
    # Consolidate and sort intervals
    consolidated_intervals = consolidate_intervals(gantt_intervals)
    for process_name, start_time, end_time in consolidated_intervals:
        print(f"{process_name} [{start_time}-{end_time}]", end=" ")
    print()
    
    # Calculate CPU utilization
    total_time = max(p.finish_time for p in processes)
    total_burst = sum(p.burst_time for p in processes)
    utilization = (total_burst / total_time) * 100
    print(f"\nCPU Utilization: {utilization:.2f}%")

def round_robin(processes, quantum):
    processes = [Process(p.pid, p.name, p.arrival_time, p.burst_time) for p in processes]
    ready_queue = deque()
    current_time = 0
    gantt_intervals = []
    completed = 0
    
    while completed < len(processes):
        # Add newly arrived processes to ready queue
        for process in processes:
            if (process.arrival_time <= current_time and 
                process.remaining_time > 0 and 
                process not in ready_queue):
                ready_queue.append(process)
        
        if not ready_queue:
            current_time += 1
            continue
            
        process = ready_queue.popleft()
        execution_time = min(quantum, process.remaining_time)
        
        # Add to Gantt chart
        gantt_intervals.append((process.name, current_time, current_time + execution_time))
        
        # Update process times
        process.remaining_time -= execution_time
        current_time += execution_time
        
        # Process completion
        if process.remaining_time == 0:
            completed += 1
            process.finish_time = current_time
            process.turnaround_time = process.finish_time - process.arrival_time
            process.waiting_time = process.turnaround_time - process.burst_time
        else:
            ready_queue.append(process)
            
    return gantt_intervals

def fcfs(processes):
    current_time = 0
    gantt_intervals = []
    processes = sorted(processes, key=lambda x: (x.arrival_time, x.pid))
    
    for process in processes:
        if current_time < process.arrival_time:
            current_time = process.arrival_time
            
        gantt_intervals.append((process.name, current_time, current_time + process.burst_time))
        current_time += process.burst_time
        process.finish_time = current_time
        process.turnaround_time = process.finish_time - process.arrival_time
        process.waiting_time = process.turnaround_time - process.burst_time
    return gantt_intervals

def srt(processes):
    processes = [Process(p.pid, p.name, p.arrival_time, p.burst_time) for p in processes]
    current_time = 0
    completed = 0
    gantt_intervals = []
    prev_process = None
    prev_start = 0
    
    while completed < len(processes):
        # Find process with shortest remaining time
        shortest = None
        shortest_time = float('inf')
        
        for process in processes:
            if (process.arrival_time <= current_time and 
                process.remaining_time > 0 and 
                process.remaining_time < shortest_time):
                shortest = process
                shortest_time = process.remaining_time
        
        if shortest is None:
            current_time += 1
            continue
            
        # Process execution
        if prev_process != shortest:
            if prev_process:
                gantt_intervals.append((prev_process.name, prev_start, current_time))
            prev_process = shortest
            prev_start = current_time
            
        shortest.remaining_time -= 1
        current_time += 1
        
        # Process completion
        if shortest.remaining_time == 0:
            completed += 1
            gantt_intervals.append((shortest.name, prev_start, current_time))
            prev_process = None
            shortest.finish_time = current_time
            shortest.turnaround_time = shortest.finish_time - shortest.arrival_time
            shortest.waiting_time = shortest.turnaround_time - shortest.burst_time
            
    return gantt_intervals

def main():
    filename = input("Enter the input file name: ")
    quantum = int(input("Enter time quantum for Round Robin: "))
    
    processes = read_processes(filename)
    
    # Run scheduling algorithms
    fcfs_intervals = fcfs(processes.copy())
    print_schedule_results(processes, "FCFS", fcfs_intervals)
    
    srt_intervals = srt(processes.copy())
    print_schedule_results(processes, "SRT", srt_intervals)
    
    rr_intervals = round_robin(processes.copy(), quantum)
    print_schedule_results(processes, "Round Robin", rr_intervals)

if __name__ == "__main__":
    main()
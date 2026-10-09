
"""
Q9: Threaded Job Scheduler Simulation
Python 3.10+

Features:
- Multiple worker threads
- Priority-based scheduling
- Arrival-time handling
- Worker assignment
- Start and finish times
- Average waiting-time calculation
"""

import heapq
from concurrent.futures import ThreadPoolExecutor


def read_jobs():
    """Read and validate job details interactively."""

    while True:
        try:
            n = int(input("How many jobs? "))
            if 1 <= n <= 20000:
                break
            print("Enter a number between 1 and 20000.")
        except ValueError:
            print("Please enter a valid whole number.")

    while True:
        try:
            workers = int(input("How many worker threads? "))
            if 1 <= workers <= 100:
                break
            print("Enter a number between 1 and 100.")
        except ValueError:
            print("Please enter a valid whole number.")

    jobs = []
    seen_ids = set()

    print("\nEnter each job in this format:")
    print("arrival_time job_id priority duration resources")

    for i in range(n):
        while True:
            try:
                parts = input(f"Job {i + 1}: ").split()

                if len(parts) != 5:
                    print("Enter exactly five fields.")
                    continue

                arrival = int(parts[0])
                job_id = parts[1]
                priority = int(parts[2])
                duration = int(parts[3])
                resources = int(parts[4])

                if arrival < 0 or duration <= 0 or resources <= 0:
                    print(
                        "Arrival must be non-negative; duration and "
                        "resources must be positive."
                    )
                    continue

                if job_id in seen_ids:
                    print("Job IDs must be unique.")
                    continue

                seen_ids.add(job_id)
                jobs.append({
                    "arrival": arrival,
                    "id": job_id,
                    "priority": priority,
                    "duration": duration,
                    "resources": resources,
                    "input_order": i,
                })
                break

            except ValueError:
                print("Invalid number. Please try again.")

    return jobs, workers


def create_schedule(jobs, worker_count):
    """
    Build a deterministic schedule.

    Higher numeric priority is scheduled first among available jobs.
    Equal priorities use arrival time and input order.
    """

    jobs = sorted(
        jobs,
        key=lambda job: (job["arrival"], job["input_order"])
    )

    # Available workers are stored as (available_time, worker_number).
    workers = [(0, i) for i in range(1, worker_count + 1)]
    heapq.heapify(workers)

    # Ready jobs use higher priority first.
    ready = []
    results = []
    next_job = 0
    current_time = 0

    while next_job < len(jobs) or ready:
        if not ready and next_job < len(jobs):
            current_time = max(current_time, jobs[next_job]["arrival"])

        # Add all jobs that have arrived by the current time.
        while (
            next_job < len(jobs)
            and jobs[next_job]["arrival"] <= current_time
        ):
            job = jobs[next_job]
            heapq.heappush(
                ready,
                (
                    -job["priority"],
                    job["arrival"],
                    job["input_order"],
                    job,
                ),
            )
            next_job += 1

        available_time, worker_number = heapq.heappop(workers)
        current_time = max(current_time, available_time)

        # A job may arrive while all workers are busy.
        while (
            next_job < len(jobs)
            and jobs[next_job]["arrival"] <= current_time
        ):
            job = jobs[next_job]
            heapq.heappush(
                ready,
                (
                    -job["priority"],
                    job["arrival"],
                    job["input_order"],
                    job,
                ),
            )
            next_job += 1

        if not ready:
            heapq.heappush(workers, (available_time, worker_number))
            continue

        _, _, _, job = heapq.heappop(ready)

        start = max(current_time, job["arrival"], available_time)
        finish = start + job["duration"]

        results.append({
            "id": job["id"],
            "worker": worker_number,
            "arrival": job["arrival"],
            "start": start,
            "finish": finish,
            "waiting": start - job["arrival"],
            "priority": job["priority"],
        })

        heapq.heappush(workers, (finish, worker_number))
        current_time = start

    return results


def execute_job(job):
    """Represent execution by a worker thread."""
    return job["id"], job["worker"]


def main():
    print("=" * 50)
    print("       THREADED JOB SCHEDULER")
    print("=" * 50)

    jobs, worker_count = read_jobs()
    schedule = create_schedule(jobs, worker_count)

    print("\nExecuting scheduled jobs using worker threads...")

    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        futures = [
            executor.submit(execute_job, job)
            for job in schedule
        ]

        # Wait for every scheduled job to complete.
        for future in futures:
            future.result()

    print("\n" + "=" * 50)
    print("SCHEDULING REPORT")
    print("=" * 50)

    # Report jobs in their original input order.
    input_order = {job["id"]: i for i, job in enumerate(jobs)}
    schedule.sort(key=lambda item: input_order[item["id"]])

    for job in schedule:
        print(
            f'{job["id"]} W{job["worker"]} '
            f'{job["start"]} {job["finish"]}'
        )

    average_wait = (
        sum(job["waiting"] for job in schedule) / len(schedule)
        if schedule else 0
    )

    print(f"AVG_WAIT {average_wait:.2f}")


if __name__ == "__main__":
    main()

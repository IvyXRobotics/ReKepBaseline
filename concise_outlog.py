from pathlib import Path

# Directory containing .log files
log_dir = Path("/home/yifan/Robotics/ReKep/output_logs")  # ← Replace this

# Prefix to keep
prefix = ">>>>>>/home/yifan/Robotics/ReKep/"

# Loop pattern definitions
loop_patterns = [
    {
        "name": "Loop pattern 7",
        "prefix_lines": (
            ">>>>>>/home/yifan/Robotics/ReKep/path_solver.py(114)objective()",
            ">>>>>>/home/yifan/Robotics/ReKep/ik_solver.py(71)solve()",
            ">>>>>>/home/yifan/Robotics/ReKep/ik_solver.py(71)solve()",
            ">>>>>>/home/yifan/Robotics/ReKep/ik_solver.py(71)solve()",
        ),
        "suffix_block": (
            ">>>>>>/home/yifan/Robotics/ReKep/environment.py(226)get_object_by_keypoint()",
            ">>>>>>/home/yifan/Robotics/ReKep/environment.py(285)is_grasping()",
        ),
        "is_variable_suffix": True,
    },
    {
        "name": "Loop pattern 1",
        "lines": (
            ">>>>>>/home/yifan/Robotics/ReKep/subgoal_solver.py(112)objective()",
            ">>>>>>/home/yifan/Robotics/ReKep/ik_solver.py(71)solve()",
        ),
    },
    {
        "name": "Loop pattern 2",
        "lines": (
            ">>>>>>/home/yifan/Robotics/ReKep/ik_solver.py(71)solve()",
            ">>>>>>/home/yifan/Robotics/ReKep/ik_solver.py(71)solve()",
            ">>>>>>/home/yifan/Robotics/ReKep/ik_solver.py(71)solve()",
            ">>>>>>/home/yifan/Robotics/ReKep/path_solver.py(114)objective()",
        ),
    },
    {
        "name": "Loop pattern 4",
        "lines": (
            ">>>>>>/home/yifan/Robotics/ReKep/environment.py(148)get_cam_obs()",
            ">>>>>>/home/yifan/Robotics/ReKep/environment.py(527)_step()",
            ">>>>>>/home/yifan/Robotics/ReKep/environment.py(482)_check_reached_ee()",
        ),
    },
    {
        "name": "Loop pattern 3",
        "lines": (
            ">>>>>>/home/yifan/Robotics/ReKep/environment.py(148)get_cam_obs()",
            ">>>>>>/home/yifan/Robotics/ReKep/environment.py(527)_step()",
        ),
    },
    {
        "name": "Loop pattern 6",
        "lines": (
            ">>>>>>/home/yifan/Robotics/ReKep/ik_solver.py(71)solve()",
            ">>>>>>/home/yifan/Robotics/ReKep/environment.py(226)get_object_by_keypoint()",
            ">>>>>>/home/yifan/Robotics/ReKep/environment.py(285)is_grasping()",
            ">>>>>>/home/yifan/Robotics/ReKep/subgoal_solver.py(112)objective()",
        ),
    },
    {
        "name": "Loop pattern 5 (suffix cleanup)",
        "lines": (
            ">>>>>>/home/yifan/Robotics/ReKep/environment.py(226)get_object_by_keypoint()",
            ">>>>>>/home/yifan/Robotics/ReKep/environment.py(285)is_grasping()",
        ),
    },
]

loop_patterns.sort(key=lambda p: -len(p.get("lines", p.get("prefix_lines", []))))
total_loops = {pattern["name"]: 0 for pattern in loop_patterns}

for log_file in log_dir.glob("*.log"):
    with log_file.open("r") as infile:
        lines = [line.strip() for line in infile if line.startswith(prefix)]

    output_lines = []
    file_loops = {pattern["name"]: 0 for pattern in loop_patterns}
    i = 0

    while i < len(lines):
        matched = False
        for pattern in loop_patterns:
            if pattern.get("is_variable_suffix"):
                prefix_lines = pattern["prefix_lines"]
                suffix_block = pattern["suffix_block"]
                prefix_len = len(prefix_lines)
                suffix_len = len(suffix_block)

                if i + prefix_len > len(lines):
                    continue

                if all(lines[i + j] == prefix_lines[j] for j in range(prefix_len)):
                    repeat_count = 0
                    j = i
                    while True:
                        if j + prefix_len > len(lines):
                            break
                        if not all(lines[j + k] == prefix_lines[k] for k in range(prefix_len)):
                            break
                        j += prefix_len
                        suffix_count = 0
                        while (
                            j + suffix_len <= len(lines)
                            and all(lines[j + k] == suffix_block[k] for k in range(suffix_len))
                        ):
                            suffix_count += 1
                            j += suffix_len
                        if suffix_count < 1:
                            break
                        repeat_count += 1
                    if repeat_count > 0:
                        output_lines.append(f"# {pattern['name']} repeated {repeat_count} times")
                        file_loops[pattern["name"]] += repeat_count
                        total_loops[pattern["name"]] += repeat_count
                        i = j
                        matched = True
                        break
            else:
                pat_lines = pattern["lines"]
                pat_len = len(pat_lines)
                count = 0
                while (
                    i + pat_len <= len(lines)
                    and all(lines[i + j] == pat_lines[j] for j in range(pat_len))
                ):
                    count += 1
                    i += pat_len
                if count >= 2:
                    output_lines.append(f"# {pattern['name']} repeated {count} times")
                    file_loops[pattern["name"]] += count
                    total_loops[pattern["name"]] += count
                    matched = True
                    break
                elif count == 1:
                    output_lines.extend(pat_lines)
                    matched = True
                    break
        if not matched:
            output_lines.append(lines[i])
            i += 1

    output_file = log_file.parent / 'concise_logs' / log_file.name.replace('.log', '.filtered.log')
    with output_file.open("w") as outfile:
        for line in output_lines:
            outfile.write(line + "\n")

    print(f"{log_file.name}:")
    for name, count in file_loops.items():
        if count > 0:
            print(f"  {name}: {count} loop(s)")

print("\nTotal loops across all files:")
for name, count in total_loops.items():
    print(f"  {name}: {count} loop(s)")

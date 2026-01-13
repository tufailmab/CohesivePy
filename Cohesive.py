# Developer: Tufail Mabood
# WhatsApp: +923440907874
# Github: Github.com/tufailmab
# Core dependencies (All Required Libraries)

import numpy as np
import os

# File & Directory Configuration

base_file = "ControlModel.inp"
"""Template input file (.inp) containing the base model definition.
Will be copied and modified for each parameter combination."""

output_dir = "czm_batch_models"
"""Output directory where all modified .inp files (one per simulation case)
and any associated output files will be written."""

log_file = "czm_assigned_values.txt"
"""Plain-text log that records which parameter values were assigned to each
generated model variant (useful for traceability and post-processing)."""

# Cohesive Zone Model (CZM) parameter bounds
# Used for Latin Hypercube / Monte Carlo / grid sampling of interface properties

n_copies = 100
"""Total number of realizations / model instances to create"""

knn_min, knn_max = 1.0, 5.0
"""KN,nn  normal (mode I) stiffness range [force/volume]"""

kss_min, kss_max = 0.1, 3.0
"""KS,ss  shear stiffness in the first shear direction (mode II)"""

ktt_min, ktt_max = 0.1, 3.0
"""KT,tt  shear stiffness in the second shear direction (mode III)"""


# Prepare output & generate parameter samples
# Create output directory (safe: won't raise error if already exists)
os.makedirs(output_dir, exist_ok=True)

# Generate evenly spaced parameter values for batch simulation
knn_vals = np.linspace(knn_min, knn_max, n_copies)  # Normal stiffness values
kss_vals = np.linspace(kss_min, kss_max, n_copies)  # Shear-s stiffness values
ktt_vals = np.linspace(ktt_min, ktt_max, n_copies)  # Shear-t stiffness values

# Read all lines from the reference Abaqus .inp file
# stored as list of strings for later modification per parameter set
with open(base_file, "r") as f:
    base_lines = f.readlines()  # list of strings, preserves original line endings

# Main batch generation: create modified .inp files for each parameter set
# open log file
log_path = os.path.join(output_dir, log_file)
with open(log_path, "w") as log:
    # CSV-style header for traceability
    log.write("Variant, knn, kss, ktt\n")

    for i in range(n_copies):

        new_lines = []          # Will hold the modified file content
        replace_next = False    # Flag: next line after *Cohesive Behavior needs replacement

        # Scan original lines and replace stiffness row when found
        for line in base_lines:
            if "*Cohesive Behavior" in line:
                replace_next = True
                new_lines.append(line)
                continue

            if replace_next:
                # Insert current sample values (scientific notation, 6 sig figs)
                new_line = f"{knn_vals[i]:.6g}, {kss_vals[i]:.6g}, {ktt_vals[i]:.6g}\n"
                new_lines.append(new_line)
                replace_next = False
            else:
                new_lines.append(line)

        # Construct variant-specific filename
        file_name = f"czmknn_kss_ktt_var{i+1}.inp"
        file_path = os.path.join(output_dir, file_name)

        # Save the new .inp file
        with open(file_path, "w") as f:
            f.writelines(new_lines)

        # Record parameters in log file
        log.write(f"var{i+1}, {knn_vals[i]:.6g}, {kss_vals[i]:.6g}, {ktt_vals[i]:.6g}\n")

        print(f"Created {file_name}")

print("Batch generation finished.")

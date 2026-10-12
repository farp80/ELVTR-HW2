## Split Policy:
**Strategy**: Stratified random split based on the *department* target label.
**Proportions**: 70% training, 15% validation, and 15% test.
**Assignment stratetgy**: The records within eachdepartment are randomly shuffle using a fixed random seed, thus to satisfy the proportions.
**Reproducibility**: A fixed random seed of 42 is used so that the same cleaned dataset produces the samepartition assignments when the code is rerun.
**Rationale**: Because this is a supervised ticket-routing classification problem, preserving the distribution of the target *department* accross partitions. Stratified split reduces the possibility that smaller departments are underrpresented in validation or test data.
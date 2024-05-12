def _mini_batch_step(X, x_squared_norms, centers, counts,
                     old_center_buffer, compute_squared_diff,
                     distances, random_reassign=False,
                     random_state=None, reassignment_ratio=.01,
                     verbose=False):
    nearest_center, inertia = _labels_inertia(X, x_squared_norms, centers,
                                              distances=distances)
    if random_reassign and reassignment_ratio > 0:
        random_state , to_reassign  = check_random_state(random_state), np.logical_or(counts <= 1, counts <= reassignment_ratio * counts.max())
        n_reassigns = min(to_reassign.sum(), X.shape[0])
        if n_reassigns:
            distances -= distances.max()
            distances *= -1
            rand_vals = random_state.rand(n_reassigns)
            rand_vals *= distances.sum()
            new_centers = np.searchsorted(distances.cumsum(),
                                          rand_vals)
            if verbose:
                print("[MiniBatchKMeans] Reassigning %i cluster centers."
                      % n_reassigns)
            if sp.issparse(X) and not sp.issparse(centers):
                assign_rows_csr(X, new_centers, np.where(to_reassign)[0],
                                centers)
            else:
                centers[to_reassign] = X[new_centers]
    if sp.issparse(X):
        return inertia, _k_means._mini_batch_update_csr(
            X, x_squared_norms, centers, counts, nearest_center,
            old_center_buffer, compute_squared_diff)
    k , squared_diff  = centers.shape[0], 0.0
    for center_idx in range(k):
        center_mask = nearest_center == center_idx
        count = center_mask.sum()
        if count > 0:
            if compute_squared_diff:
                old_center_buffer[:] = centers[center_idx]
            centers[center_idx] *= counts[center_idx]
            centers[center_idx] += np.sum(X[center_mask], axis=0)
            counts[center_idx] += count
            centers[center_idx] /= counts[center_idx]
            if compute_squared_diff:
                diff = centers[center_idx].ravel() - old_center_buffer.ravel()
                squared_diff += np.dot(diff, diff)
    return inertia, squared_diff

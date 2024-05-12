def load_app(self):
    if self._loaded_app is not None:
        return self._loaded_app
    if self.create_app is not None:
        app = self.create_app()
    else:
        if self.app_import_path:
            path, name = (
                re.split(r":(?![\\/])", self.app_import_path, 1) + [None]
            )[:2]
            import_name = prepare_import(path)
            app = locate_app(import_name, name)
        else:
            for path in ("wsgi.py", "app.py"):
                import_name = prepare_import(path)
                app = locate_app(import_name, None, raise_if_not_found=False)
                if app:
                    break
    if not app:
        raise NoAppException(
            "Could not locate a Flask application. Use the"
            " 'flask --app' option, 'FLASK_APP' environment"
            " variable, or a 'wsgi.py' or 'app.py' file in the"
            " current directory."
        )
    if self.set_debug_flag:
        app.debug = get_debug_flag()
    self._loaded_app = app
    return app

def run_async(func):
    try:
        from asgiref.sync import async_to_sync
    except ImportError:
        raise RuntimeError(
            "Install Flask with the 'async' extra in order to use async views."
        )
    if ContextVar.__module__ == "werkzeug.local":
        raise RuntimeError(
            "Async cannot be used with this combination of Python & Greenlet versions."
        )
    def outer(*args, **kwargs):
        ctx = None
        if _request_ctx_stack.top is not None:
            ctx = _request_ctx_stack.top.copy()
        async def inner(*a, **k):
            if ctx is not None:
                with ctx:
                    return await func(*a, **k)
            else:
                return await func(*a, **k)
        return async_to_sync(inner)(*args, **kwargs)
    outer._flask_sync_wrapper = True  
    return outer

def jsonify(*args, **kwargs):
    indent = None
    separators = (',', ':')
    if current_app.config['JSONIFY_PRETTYPRINT_REGULAR'] or current_app.debug:
        indent = 2
        separators = (', ', ': ')
    if args and kwargs:
        raise TypeError('jsonify() behavior undefined when passed both args and kwargs')
    elif len(args) == 1:  
        data = args[0]
    else:
        data = args or kwargs
    return current_app.response_class(
        (dumps(data, indent=indent, separators=separators), '\n'),
        mimetype=current_app.config['JSONIFY_MIMETYPE']
    )

def handle_user_exception(self, e):
    exc_type, exc_value, tb = sys.exc_info()
    assert exc_value is e
    if (
        self.debug or self.config['TRAP_BAD_REQUEST_ERRORS']
        and isinstance(e, BadRequestKeyError)
        and e.description is BadRequestKeyError.description
    ):
        e.description = "KeyError: '{0}'".format(*e.args)
    if isinstance(e, HTTPException) and not self.trap_http_exception(e):
        return self.handle_http_exception(e)
    handler = self._find_error_handler(e)
    if handler is None:
        reraise(exc_type, exc_value, tb)
    return handler(e)

def retroactive_resolution(
    coefficients, vector
):
    rows, columns = np.shape(coefficients)
    x = np.zeros((rows, 1), dtype=float)
    for row in reversed(range(rows)):
        total = np.dot(coefficients[row, row + 1 :], x[row + 1 :])
        x[row, 0] = (vector[row] - total) / coefficients[row, row]
    return x

def _lars_path_solver(
    X,
    y,
    Xy=None,
    Gram=None,
    n_samples=None,
    max_iter=500,
    alpha_min=0,
    method="lar",
    copy_X=True,
    eps=np.finfo(float).eps,
    copy_Gram=True,
    verbose=0,
    return_path=True,
    return_n_iter=False,
    positive=False,
):
    if method == "lar" and positive:
        raise ValueError("Positive constraint not supported for 'lar' coding method.")
    n_samples = n_samples if n_samples is not None else y.size
    if Xy is None:
        Cov = np.dot(X.T, y)
    else:
        Cov = Xy.copy()
    if Gram is None or Gram is False:
        Gram = None
        if X is None:
            raise ValueError("X and Gram cannot both be unspecified.")
    elif isinstance(Gram, str) and Gram == "auto" or Gram is True:
        if Gram is True or X.shape[0] > X.shape[1]:
            Gram = np.dot(X.T, X)
        else:
            Gram = None
    elif copy_Gram:
        Gram = Gram.copy()
    if Gram is None:
        n_features = X.shape[1]
    else:
        n_features = Cov.shape[0]
        if Gram.shape != (n_features, n_features):
            raise ValueError("The shapes of the inputs Gram and Xy do not match.")
    if copy_X and X is not None and Gram is None:
        X = X.copy("F")
    max_features = min(max_iter, n_features)
    dtypes = set(a.dtype for a in (X, y, Xy, Gram) if a is not None)
    if len(dtypes) == 1:
        return_dtype = next(iter(dtypes))
    else:
        return_dtype = np.float64
    if return_path:
        coefs = np.zeros((max_features + 1, n_features), dtype=return_dtype)
        alphas = np.zeros(max_features + 1, dtype=return_dtype)
    else:
        coef, prev_coef = (
            np.zeros(n_features, dtype=return_dtype),
            np.zeros(n_features, dtype=return_dtype),
        )
        alpha, prev_alpha = (
            np.array([0.0], dtype=return_dtype),
            np.array([0.0], dtype=return_dtype),
        )
    n_iter, n_active = 0, 0
    active, indices = list(), np.arange(n_features)
    sign_active = np.empty(max_features, dtype=np.int8)
    drop = False
    if Gram is None:
        L = np.empty((max_features, max_features), dtype=X.dtype)
        swap, nrm2 = linalg.get_blas_funcs(("swap", "nrm2"), (X,))
    else:
        L = np.empty((max_features, max_features), dtype=Gram.dtype)
        swap, nrm2 = linalg.get_blas_funcs(("swap", "nrm2"), (Cov,))
    (solve_cholesky,) = get_lapack_funcs(("potrs",), (L,))
    if verbose:
        if verbose > 1:
            print("Step\t\tAdded\t\tDropped\t\tActive set size\t\tC")
        else:
            sys.stdout.write(".")
            sys.stdout.flush()
    tiny32 = np.finfo(np.float32).tiny  
    cov_precision = np.finfo(Cov.dtype).precision
    equality_tolerance = np.finfo(np.float32).eps
    if Gram is not None:
        Gram_copy = Gram.copy()
        Cov_copy = Cov.copy()
    while True:
        if Cov.size:
            if positive:
                C_idx = np.argmax(Cov)
            else:
                C_idx = np.argmax(np.abs(Cov))
            C_ = Cov[C_idx]
            if positive:
                C = C_
            else:
                C = np.fabs(C_)
        else:
            C = 0.0
        if return_path:
            alpha = alphas[n_iter, np.newaxis]
            coef = coefs[n_iter]
            prev_alpha = alphas[n_iter - 1, np.newaxis]
            prev_coef = coefs[n_iter - 1]
        alpha[0] = C / n_samples
        if alpha[0] <= alpha_min + equality_tolerance:  
            if abs(alpha[0] - alpha_min) > equality_tolerance:
                if n_iter > 0:
                    ss = (prev_alpha[0] - alpha_min) / (prev_alpha[0] - alpha[0])
                    coef[:] = prev_coef + ss * (coef - prev_coef)
                alpha[0] = alpha_min
            if return_path:
                coefs[n_iter] = coef
            break
        if n_iter >= max_iter or n_active >= n_features:
            break
        if not drop:
            if positive:
                sign_active[n_active] = np.ones_like(C_)
            else:
                sign_active[n_active] = np.sign(C_)
            m, n = n_active, C_idx + n_active
            Cov[C_idx], Cov[0] = swap(Cov[C_idx], Cov[0])
            indices[n], indices[m] = indices[m], indices[n]
            Cov_not_shortened = Cov
            Cov = Cov[1:]  
            if Gram is None:
                X.T[n], X.T[m] = swap(X.T[n], X.T[m])
                c = nrm2(X.T[n_active]) ** 2
                L[n_active, :n_active] = np.dot(X.T[n_active], X.T[:n_active].T)
            else:
                Gram[m], Gram[n] = swap(Gram[m], Gram[n])
                Gram[:, m], Gram[:, n] = swap(Gram[:, m], Gram[:, n])
                c = Gram[n_active, n_active]
                L[n_active, :n_active] = Gram[n_active, :n_active]
            if n_active:
                linalg.solve_triangular(
                    L[:n_active, :n_active],
                    L[n_active, :n_active],
                    trans=0,
                    lower=1,
                    overwrite_b=True,
                    **SOLVE_TRIANGULAR_ARGS,
                )
            v = np.dot(L[n_active, :n_active], L[n_active, :n_active])
            diag = max(np.sqrt(np.abs(c - v)), eps)
            L[n_active, n_active] = diag
            if diag < 1e-7:
                warnings.warn(
                    "Regressors in active set degenerate. "
                    "Dropping a regressor, after %i iterations, "
                    "i.e. alpha=%.3e, "
                    "with an active set of %i regressors, and "
                    "the smallest cholesky pivot element being %.3e."
                    " Reduce max_iter or increase eps parameters."
                    % (n_iter, alpha, n_active, diag),
                    ConvergenceWarning,
                )
                Cov = Cov_not_shortened
                Cov[0] = 0
                Cov[C_idx], Cov[0] = swap(Cov[C_idx], Cov[0])
                continue
            active.append(indices[n_active])
            n_active += 1
            if verbose > 1:
                print(
                    "%s\t\t%s\t\t%s\t\t%s\t\t%s" % (n_iter, active[-1], "", n_active, C)
                )
        if method == "lasso" and n_iter > 0 and prev_alpha[0] < alpha[0]:
            warnings.warn(
                "Early stopping the lars path, as the residues "
                "are small and the current value of alpha is no "
                "longer well controlled. %i iterations, alpha=%.3e, "
                "previous alpha=%.3e, with an active set of %i "
                "regressors." % (n_iter, alpha, prev_alpha, n_active),
                ConvergenceWarning,
            )
            break
        least_squares, _ = solve_cholesky(
            L[:n_active, :n_active], sign_active[:n_active], lower=True
        )
        if least_squares.size == 1 and least_squares == 0:
            least_squares[...] = 1
            AA = 1.0
        else:
            AA = 1.0 / np.sqrt(np.sum(least_squares * sign_active[:n_active]))
            if not np.isfinite(AA):
                i = 0
                L_ = L[:n_active, :n_active].copy()
                while not np.isfinite(AA):
                    L_.flat[:: n_active + 1] += (2**i) * eps
                    least_squares, _ = solve_cholesky(
                        L_, sign_active[:n_active], lower=True
                    )
                    tmp = max(np.sum(least_squares * sign_active[:n_active]), eps)
                    AA = 1.0 / np.sqrt(tmp)
                    i += 1
            least_squares *= AA
        if Gram is None:
            eq_dir = np.dot(X.T[:n_active].T, least_squares)
            corr_eq_dir = np.dot(X.T[n_active:], eq_dir)
        else:
            corr_eq_dir = np.dot(Gram[:n_active, n_active:].T, least_squares)
        np.around(corr_eq_dir, decimals=cov_precision, out=corr_eq_dir)
        g1 = arrayfuncs.min_pos((C - Cov) / (AA - corr_eq_dir + tiny32))
        if positive:
            gamma_ = min(g1, C / AA)
        else:
            g2 = arrayfuncs.min_pos((C + Cov) / (AA + corr_eq_dir + tiny32))
            gamma_ = min(g1, g2, C / AA)
        drop = False
        z = -coef[active] / (least_squares + tiny32)
        z_pos = arrayfuncs.min_pos(z)
        if z_pos < gamma_:
            idx = np.where(z == z_pos)[0][::-1]
            sign_active[idx] = -sign_active[idx]
            if method == "lasso":
                gamma_ = z_pos
            drop = True
        n_iter += 1
        if return_path:
            if n_iter >= coefs.shape[0]:
                del coef, alpha, prev_alpha, prev_coef
                add_features = 2 * max(1, (max_features - n_active))
                coefs = np.resize(coefs, (n_iter + add_features, n_features))
                coefs[-add_features:] = 0
                alphas = np.resize(alphas, n_iter + add_features)
                alphas[-add_features:] = 0
            coef = coefs[n_iter]
            prev_coef = coefs[n_iter - 1]
        else:
            prev_coef = coef
            prev_alpha[0] = alpha[0]
            coef = np.zeros_like(coef)
        coef[active] = prev_coef[active] + gamma_ * least_squares
        Cov -= gamma_ * corr_eq_dir
        if drop and method == "lasso":
            for ii in idx:
                arrayfuncs.cholesky_delete(L[:n_active, :n_active], ii)
            n_active -= 1
            drop_idx = [active.pop(ii) for ii in idx]
            if Gram is None:
                for ii in idx:
                    for i in range(ii, n_active):
                        X.T[i], X.T[i + 1] = swap(X.T[i], X.T[i + 1])
                        indices[i], indices[i + 1] = indices[i + 1], indices[i]
                residual = y - np.dot(X[:, :n_active], coef[active])
                temp = np.dot(X.T[n_active], residual)
                Cov = np.r_[temp, Cov]
            else:
                for ii in idx:
                    for i in range(ii, n_active):
                        indices[i], indices[i + 1] = indices[i + 1], indices[i]
                        Gram[i], Gram[i + 1] = swap(Gram[i], Gram[i + 1])
                        Gram[:, i], Gram[:, i + 1] = swap(Gram[:, i], Gram[:, i + 1])
                temp = Cov_copy[drop_idx] - np.dot(Gram_copy[drop_idx], coef)
                Cov = np.r_[temp, Cov]
            sign_active = np.delete(sign_active, idx)
            sign_active = np.append(sign_active, 0.0)  
            if verbose > 1:
                print(
                    "%s\t\t%s\t\t%s\t\t%s\t\t%s"
                    % (n_iter, "", drop_idx, n_active, abs(temp))
                )
    if return_path:
        alphas = alphas[: n_iter + 1]
        coefs = coefs[: n_iter + 1]
        if return_n_iter:
            return alphas, active, coefs.T, n_iter
        else:
            return alphas, active, coefs.T
    else:
        if return_n_iter:
            return alpha, active, coef, n_iter
        else:
            return alpha, active, coef

def _solve_sparse_cg(
    X,
    y,
    alpha,
    max_iter=None,
    tol=1e-4,
    verbose=0,
    X_offset=None,
    X_scale=None,
    sample_weight_sqrt=None,
):
    if sample_weight_sqrt is None:
        sample_weight_sqrt = np.ones(X.shape[0], dtype=X.dtype)
    n_samples, n_features = X.shape
    if X_offset is None or X_scale is None:
        X1 = sp_linalg.aslinearoperator(X)
    else:
        X_offset_scale = X_offset / X_scale
        X1 = _get_rescaled_operator(X, X_offset_scale, sample_weight_sqrt)
    coefs = np.empty((y.shape[1], n_features), dtype=X.dtype)
    if n_features > n_samples:
        def create_mv(curr_alpha):
            def _mv(x):
                return X1.matvec(X1.rmatvec(x)) + curr_alpha * x
            return _mv
    else:
        def create_mv(curr_alpha):
            def _mv(x):
                return X1.rmatvec(X1.matvec(x)) + curr_alpha * x
            return _mv
    for i in range(y.shape[1]):
        y_column = y[:, i]
        mv = create_mv(alpha[i])
        if n_features > n_samples:
            C = sp_linalg.LinearOperator(
                (n_samples, n_samples), matvec=mv, dtype=X.dtype
            )
            try:
                coef, info = sp_linalg.cg(C, y_column, tol=tol, atol="legacy")
            except TypeError:
                coef, info = sp_linalg.cg(C, y_column, tol=tol)
            coefs[i] = X1.rmatvec(coef)
        else:
            y_column = X1.rmatvec(y_column)
            C = sp_linalg.LinearOperator(
                (n_features, n_features), matvec=mv, dtype=X.dtype
            )
            try:
                coefs[i], info = sp_linalg.cg(
                    C, y_column, maxiter=max_iter, tol=tol, atol="legacy"
                )
            except TypeError:
                coefs[i], info = sp_linalg.cg(C, y_column, maxiter=max_iter, tol=tol)
        if info < 0:
            raise ValueError("Failed with error code %d" % info)
        if max_iter is None and info > 0 and verbose:
            warnings.warn(
                "sparse_cg did not converge after %d iterations." % info,
                ConvergenceWarning,
            )
    return coefs

def json(self):
    if self._cached_decoded_json is _NONE:
        self._cached_decoded_json = json.loads(self.text)
    return self._cached_decoded_json

async def create_triggers(self):
    while self.to_create:
        trigger_id, trigger_instance = self.to_create.popleft()
        if trigger_id not in self.triggers:
            task_instance = trigger_instance.task_instance
            dag_id = task_instance.dag_id
            run_id = task_instance.run_id
            task_id = task_instance.task_id
            map_index = task_instance.map_index
            try_number = task_instance.try_number
            self.triggers[trigger_id] = {
                "task": asyncio.create_task(self.run_trigger(trigger_id, trigger_instance)),
                "name": f"{dag_id}/{run_id}/{task_id}/{map_index}/{try_number} (ID {trigger_id})",
                "events": 0,
            }
        else:
            self.log.warning("Trigger %s had insertion attempted twice", trigger_id)
        await asyncio.sleep(0)

def generate_back_references(link, base_path):
    is_downloaded, file_name = download_file(link)
    if not is_downloaded:
        old_to_new = []
    else:
        print(f"Constructs old to new mapping from redirects.txt for {base_path}")
        old_to_new = construct_old_to_new_tuple_mapping(file_name)
    old_to_new.append(("index.html", "changelog.html"))
    old_to_new.append(("index.html", "security.html"))
    old_to_new.append(("security.html", "security/security-model.html"))
    for versioned_provider_path in (p for p in base_path.iterdir() if p.is_dir()):
        print(f"Processing {base_path}, version: {versioned_provider_path.name}")
        for old, new in old_to_new:
            if (versioned_provider_path / old).exists():
                split_new_path, file_name = new.rsplit("/", 1)
                dest_dir = versioned_provider_path / split_new_path
                relative_path = os.path.relpath(old, new)
                relative_path = relative_path.replace("../", "", 1)
                os.makedirs(dest_dir, exist_ok=True)
                dest_file_path = dest_dir / file_name
                create_back_reference_html(relative_path, dest_file_path)

def _iter_member_names(klass):
    for node in ast.iter_child_nodes(klass):
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            yield node.target.id
        elif isinstance(node, ast.FunctionDef) and _is_property(node):
            yield node.name
        elif isinstance(node, ast.Assign):
            if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                yield node.targets[0].id

def _find_executable_task_instances(self, simple_dag_bag, states, session=None):
    states_to_count_as_running = [State.RUNNING]
    executable_tis = []
    TI = models.TaskInstance
    DR = models.DagRun
    DM = models.DagModel
    ti_query = (
        session
        .query(TI)
        .filter(TI.dag_id.in_(simple_dag_bag.dag_ids))
        .outerjoin(DR,
            and_(DR.dag_id == TI.dag_id,
                 DR.execution_date == TI.execution_date))
        .filter(or_(DR.run_id == None,
                not_(DR.run_id.like(BackfillJob.ID_PREFIX + '%'))))
        .outerjoin(DM, DM.dag_id==TI.dag_id)
        .filter(or_(DM.dag_id == None,
                not_(DM.is_paused)))
    )
    if None in states:
        ti_query = ti_query.filter(or_(TI.state == None, TI.state.in_(states)))
    else:
        ti_query = ti_query.filter(TI.state.in_(states))
    task_instances_to_examine = ti_query.all()
    if len(task_instances_to_examine) == 0:
        self.log.info("No tasks to consider for execution.")
        return executable_tis
    task_instance_str = "\n\t".join(
        ["{}".format(x) for x in task_instances_to_examine])
    self.log.info("Tasks up for execution:\n\t%s", task_instance_str)
    pools = {p.pool: p for p in session.query(models.Pool).all()}
    pool_to_task_instances = defaultdict(list)
    for task_instance in task_instances_to_examine:
        pool_to_task_instances[task_instance.pool].append(task_instance)
    task_concurrency_map = self.__get_task_concurrency_map(states=states_to_count_as_running, session=session)
    for pool, task_instances in pool_to_task_instances.items():
        if not pool:
            open_slots = conf.getint('core', 'non_pooled_task_slot_count')
        else:
            if pool not in pools:
                self.log.warning(
                    "Tasks using non-existent pool '%s' will not be scheduled",
                    pool
                )
                open_slots = 0
            else:
                open_slots = pools[pool].open_slots(session=session)
        num_queued = len(task_instances)
        self.log.info(
            "Figuring out tasks to run in Pool(name={pool}) with {open_slots} "
            "open slots and {num_queued} task instances in queue".format(
                **locals()
            )
        )
        priority_sorted_task_instances = sorted(
            task_instances, key=lambda ti: (-ti.priority_weight, ti.execution_date))
        dag_id_to_possibly_running_task_count = {}
        for task_instance in priority_sorted_task_instances:
            if open_slots <= 0:
                self.log.info(
                    "Not scheduling since there are %s open slots in pool %s",
                    open_slots, pool
                )
                break
            dag_id = task_instance.dag_id
            simple_dag = simple_dag_bag.get_dag(dag_id)
            if dag_id not in dag_id_to_possibly_running_task_count:
                dag_id_to_possibly_running_task_count[dag_id] = \
                        DAG.get_num_task_instances(
                        dag_id,
                        simple_dag_bag.get_dag(dag_id).task_ids,
                        states=states_to_count_as_running,
                        session=session)
            current_task_concurrency = dag_id_to_possibly_running_task_count[dag_id]
            task_concurrency_limit = simple_dag_bag.get_dag(dag_id).concurrency
            self.log.info(
                "DAG %s has %s/%s running and queued tasks",
                dag_id, current_task_concurrency, task_concurrency_limit
            )
            if current_task_concurrency >= task_concurrency_limit:
                self.log.info(
                    "Not executing %s since the number of tasks running or queued from DAG %s"
                    " is >= to the DAG's task concurrency limit of %s",
                    task_instance, dag_id, task_concurrency_limit
                )
                continue
            task_concurrency = simple_dag.get_task_special_arg(task_instance.task_id, 'task_concurrency')
            if task_concurrency is not None:
                num_running = task_concurrency_map[((task_instance.dag_id, task_instance.task_id))]
                if num_running >= task_concurrency:
                    self.logger.info("Not executing %s since the task concurrency for this task"
                                     " has been reached.", task_instance)
                    continue
                else:
                    task_concurrency_map[(task_instance.dag_id, task_instance.task_id)] += 1
            if self.executor.has_task(task_instance):
                self.log.debug(
                    "Not handling task %s as the executor reports it is running",
                    task_instance.key
                )
                continue
            executable_tis.append(task_instance)
            open_slots -= 1
            dag_id_to_possibly_running_task_count[dag_id] += 1
    task_instance_str = "\n\t".join(
        ["{}".format(x) for x in executable_tis])
    self.log.info("Setting the follow tasks to queued state:\n\t%s", task_instance_str)
    for ti in executable_tis:
        copy_dag_id = ti.dag_id
        copy_execution_date = ti.execution_date
        copy_task_id = ti.task_id
        make_transient(ti)
        ti.dag_id = copy_dag_id
        ti.execution_date = copy_execution_date
        ti.task_id = copy_task_id
    return executable_tis

def process_file(self, file_path, pickle_dags=False, session=None):
    self.logger.info("Processing file %s for tasks to queue", file_path)
    simple_dags = []
    try:
        dagbag = models.DagBag(file_path)
    except Exception:
        self.logger.exception("Failed at reloading the DAG file %s", file_path)
        Stats.incr('dag_file_refresh_error', 1, 1)
        return []
    if len(dagbag.dags) > 0:
        self.logger.info("DAG(s) %s retrieved from %s", dagbag.dags.keys(), file_path)
    else:
        self.logger.warning("No viable dags retrieved from %s", file_path)
        self.update_import_errors(session, dagbag)
        return []
    sync_time = datetime.now()
    for dag in dagbag.dags.values():
        models.DAG.sync_to_db(dag, dag.owner, sync_time)
    paused_dag_ids = [dag.dag_id for dag in dagbag.dags.values()
                      if dag.is_paused]
    for dag_id in dagbag.dags:
        dag = dagbag.get_dag(dag_id)
        pickle_id = None
        if pickle_dags:
            pickle_id = dag.pickle(session).id
        task_ids = [task.task_id for task in dag.tasks]
        if dag_id not in paused_dag_ids:
            simple_dags.append(SimpleDag(dag.dag_id,
                                         task_ids,
                                         dag.full_filepath,
                                         dag.concurrency,
                                         dag.is_paused,
                                         pickle_id))
    if len(self.dag_ids) > 0:
        dags = [dag for dag in dagbag.dags.values()
                if dag.dag_id in self.dag_ids and
                dag.dag_id not in paused_dag_ids]
    else:
        dags = [dag for dag in dagbag.dags.values()
                if not dag.parent_dag and
                dag.dag_id not in paused_dag_ids]
    ti_keys_to_schedule = []
    self._process_dags(dagbag, dags, ti_keys_to_schedule)
    for ti_key in ti_keys_to_schedule:
        dag = dagbag.dags[ti_key[0]]
        task = dag.get_task(ti_key[1])
        ti = models.TaskInstance(task, ti_key[2])
        ti.refresh_from_db(session=session, lock_for_update=True)
        dep_context = DepContext(deps=QUEUE_DEPS, ignore_task_deps=True)
        if ti.are_dependencies_met(
                dep_context=dep_context,
                session=session,
                verbose=True):
            ti.state = State.SCHEDULED
        self.logger.info("Creating / updating %s in ORM", ti)
        session.merge(ti)
        session.commit()
    try:
        self.update_import_errors(session, dagbag)
    except Exception:
        self.logger.exception("Error logging import errors!")
    try:
        dagbag.kill_zombies()
    except Exception:
        self.logger.exception("Error killing zombies!")
    return simple_dags

def _maybe_empty_lines_for_class_or_def(
    self, current_line, before
):
    if not current_line.is_decorator:
        self.previous_defs.append(current_line.depth)
    if self.previous_line is None:
        return 0, 0
    if self.previous_line.is_decorator:
        if self.is_pyi and current_line.is_stub_class:
            return 0, 1
        return 0, 0
    if self.previous_line.depth < current_line.depth and (
        self.previous_line.is_class or self.previous_line.is_def
    ):
        return 0, 0
    if (
        self.previous_line.is_comment
        and self.previous_line.depth == current_line.depth
        and before == 0
    ):
        return 0, 0
    if self.is_pyi:
        if self.previous_line.depth > current_line.depth:
            newlines = 1
        elif current_line.is_class or self.previous_line.is_class:
            if current_line.is_stub_class and self.previous_line.is_stub_class:
                newlines = 0
            else:
                newlines = 1
        elif (
            current_line.is_def or current_line.is_decorator
        ) and not self.previous_line.is_def:
            if not current_line.depth:
                newlines = 1
            else:
                newlines = min(2, before + 1)
        else:
            newlines = 0
    else:
        newlines = 2
    if current_line.depth and newlines:
        newlines -= 1
    return newlines, 0

def aggregate(obj, arg, *args, **kwargs):
    is_aggregator = lambda x: isinstance(x, (list, tuple, dict))
    _axis = kwargs.pop("_axis", None)
    if _axis is None:
        _axis = getattr(obj, "axis", 0)
    if isinstance(arg, str):
        return obj._try_aggregate_string_function(arg, *args, **kwargs), None
    if isinstance(arg, dict):
        if _axis != 0:  
            raise ValueError("Can only pass dict with axis=0")
        selected_obj = obj._selected_obj
        if any(is_aggregator(x) for x in arg.values()):
            new_arg = {}
            for k, v in arg.items():
                if not isinstance(v, (tuple, list, dict)):
                    new_arg[k] = [v]
                else:
                    new_arg[k] = v
                if isinstance(v, dict):
                    raise SpecificationError("nested renamer is not supported")
                elif isinstance(selected_obj, ABCSeries):
                    raise SpecificationError("nested renamer is not supported")
                elif (
                    isinstance(selected_obj, ABCDataFrame)
                    and k not in selected_obj.columns
                ):
                    raise KeyError(f"Column '{k}' does not exist!")
            arg = new_arg
        else:
            keys = list(arg.keys())
            if isinstance(selected_obj, ABCDataFrame) and len(
                selected_obj.columns.intersection(keys)
            ) != len(keys):
                cols = sorted(set(keys) - set(selected_obj.columns.intersection(keys)))
                raise SpecificationError(f"Column(s) {cols} do not exist")
        from pandas.core.reshape.concat import concat
        def _agg_1dim(name, how, subset=None):
            colg = obj._gotitem(name, ndim=1, subset=subset)
            if colg.ndim != 1:
                raise SpecificationError(
                    "nested dictionary is ambiguous in aggregation"
                )
            return colg.aggregate(how)
        def _agg_2dim(how):
            colg = obj._gotitem(obj._selection, ndim=2, subset=selected_obj)
            return colg.aggregate(how)
        def _agg(arg, func):
            result = {}
            for fname, agg_how in arg.items():
                result[fname] = func(fname, agg_how)
            return result
        keys = list(arg.keys())
        if obj._selection is not None:
            sl = set(obj._selection_list)
            if len(sl) == 1:
                result = _agg(
                    arg, lambda fname, agg_how: _agg_1dim(obj._selection, agg_how)
                )
            elif not len(sl - set(keys)):
                result = _agg(arg, _agg_1dim)
            else:
                result = _agg(arg, _agg_2dim)
        else:
            try:
                result = _agg(arg, _agg_1dim)
            except SpecificationError:
                result = _agg(arg, _agg_2dim)
        def is_any_series():
            return any(isinstance(r, ABCSeries) for r in result.values())
        def is_any_frame():
            return any(isinstance(r, ABCDataFrame) for r in result.values())
        if isinstance(result, list):
            return concat(result, keys=keys, axis=1, sort=True), True
        elif is_any_frame():
            keys_to_use = [k for k in keys if not result[k].empty]
            keys_to_use = keys_to_use if keys_to_use != [] else keys
            return (
                concat([result[k] for k in keys_to_use], keys=keys_to_use, axis=1),
                True,
            )
        elif isinstance(obj, ABCSeries) and is_any_series():
            try:
                result = concat(result)
            except TypeError as err:
                raise ValueError(
                    "cannot perform both aggregation "
                    "and transformation operations "
                    "simultaneously"
                ) from err
            return result, True
        from pandas import DataFrame, Series
        try:
            result = DataFrame(result)
        except ValueError:
            if obj.ndim == 1:
                obj = cast("Series", obj)
                name = obj.name
            else:
                name = None
            result = Series(result, name=name)
        return result, True
    elif is_list_like(arg):
        return aggregate_multiple_funcs(obj, arg, _axis=_axis), None
    else:
        result = None
    if callable(arg):
        f = obj._get_cython_func(arg)
        if f and not args and not kwargs:
            return getattr(obj, f)(), None
    return result, True

def _get_grouper_for_level(self, mapper, level):
    indexer = self.codes[level]
    level_index = self.levels[level]
    if mapper is not None:
        level_values = self.levels[level].take(indexer)
        grouper = level_values.map(mapper)
        return grouper, None, None
    codes, uniques = algos.factorize(indexer, sort=True)
    if len(uniques) > 0 and uniques[0] == -1:
        mask = indexer != -1
        ok_codes, uniques = algos.factorize(indexer[mask], sort=True)
        codes = np.empty(len(indexer), dtype=indexer.dtype)
        codes[mask] = ok_codes
        codes[~mask] = -1
    if len(uniques) < len(level_index):
        level_index = level_index.take(uniques)
    else:
        level_index = level_index.copy()
    if len(level_index):
        grouper = level_index.take(codes)
    else:
        grouper = level_index.take(codes, fill_value=True)
    return grouper, codes, level_index

def maybe_promote(dtype, fill_value=np.nan):
    if isinstance(fill_value, np.ndarray):
        if issubclass(fill_value.dtype.type, (np.datetime64, np.timedelta64)):
            fill_value = fill_value.dtype.type("NaT", "ns")
        else:
            if fill_value.dtype == np.object_:
                dtype = np.dtype(np.object_)
            fill_value = np.nan
        if dtype == np.object_ or dtype.kind in ["U", "S"]:
            fill_value = np.nan
            dtype = np.dtype(np.object_)
    if issubclass(dtype.type, np.datetime64):
        if isinstance(fill_value, datetime) and fill_value.tzinfo is not None:
            dtype = np.dtype(np.object_)
        elif is_integer(fill_value) or (is_float(fill_value) and not isna(fill_value)):
            dtype = np.dtype(np.object_)
        else:
            try:
                fill_value = tslibs.Timestamp(fill_value).to_datetime64()
            except (TypeError, ValueError):
                dtype = np.dtype(np.object_)
    elif issubclass(dtype.type, np.timedelta64):
        if (
            is_integer(fill_value)
            or (is_float(fill_value) and not np.isnan(fill_value))
            or isinstance(fill_value, str)
        ):
            dtype = np.dtype(np.object_)
        else:
            try:
                fv = tslibs.Timedelta(fill_value)
            except ValueError:
                dtype = np.dtype(np.object_)
            else:
                if fv is NaT:
                    fill_value = np.timedelta64("NaT", "ns")
                else:
                    fill_value = fv.to_timedelta64()
    elif is_datetime64tz_dtype(dtype):
        if isna(fill_value):
            fill_value = NaT
    elif is_extension_array_dtype(dtype) and isna(fill_value):
        fill_value = dtype.na_value
    elif is_float(fill_value):
        if issubclass(dtype.type, np.bool_):
            dtype = np.object_
        elif issubclass(dtype.type, np.integer):
            dtype = np.dtype(np.float64)
            if not isna(fill_value):
                fill_value = dtype.type(fill_value)
        elif dtype.kind == "f":
            if not np.can_cast(fill_value, dtype):
                dtype = np.min_scalar_type(fill_value)
        elif dtype.kind == "c":
            if not np.can_cast(fill_value, dtype):
                if np.can_cast(fill_value, np.dtype("c16")):
                    dtype = np.dtype(np.complex128)
                else:
                    dtype = np.dtype(np.object_)
            if dtype.kind == "c" and not np.isnan(fill_value):
                fill_value = dtype.type(fill_value)
    elif is_bool(fill_value):
        if not issubclass(dtype.type, np.bool_):
            dtype = np.object_
        else:
            fill_value = np.bool_(fill_value)
    elif is_integer(fill_value):
        if issubclass(dtype.type, np.bool_):
            dtype = np.dtype(np.object_)
        elif issubclass(dtype.type, np.integer):
            if not np.can_cast(fill_value, dtype):
                mst = np.min_scalar_type(fill_value)
                dtype = np.promote_types(dtype, mst)
                if dtype.kind == "f":
                    dtype = np.dtype(np.object_)
            fill_value = dtype.type(fill_value)
        elif issubclass(dtype.type, np.floating):
            if _check_lossless_cast(fill_value, dtype):
                fill_value = dtype.type(fill_value)
        if dtype.kind in ["c", "f"]:
            fill_value = dtype.type(fill_value)
    elif is_complex(fill_value):
        if issubclass(dtype.type, np.bool_):
            dtype = np.dtype(np.object_)
        elif issubclass(dtype.type, (np.integer, np.floating)):
            c8 = np.dtype(np.complex64)
            info = np.finfo(dtype) if dtype.kind == "f" else np.iinfo(dtype)
            if (
                np.can_cast(fill_value, c8)
                and np.can_cast(info.min, c8)
                and np.can_cast(info.max, c8)
            ):
                dtype = np.dtype(np.complex64)
            else:
                dtype = np.dtype(np.complex128)
        elif dtype.kind == "c":
            mst = np.min_scalar_type(fill_value)
            if mst > dtype and mst.kind == "c":
                dtype = mst
        if dtype.kind == "c":
            fill_value = dtype.type(fill_value)
    elif fill_value is None:
        if is_float_dtype(dtype) or is_complex_dtype(dtype):
            fill_value = np.nan
        elif is_integer_dtype(dtype):
            dtype = np.float64
            fill_value = np.nan
        elif is_datetime_or_timedelta_dtype(dtype):
            fill_value = dtype.type("NaT", "ns")
        else:
            dtype = np.object_
            fill_value = np.nan
    else:
        dtype = np.object_
    if is_extension_array_dtype(dtype):
        pass
    elif issubclass(np.dtype(dtype).type, (bytes, str)):
        dtype = np.object_
    return dtype, fill_value

def maybe_promote(dtype, fill_value=np.nan):
    if isinstance(fill_value, np.ndarray):
        if issubclass(fill_value.dtype.type, (np.datetime64, np.timedelta64)):
            fill_value = fill_value.dtype.type("NaT", "ns")
        else:
            if fill_value.dtype == np.object_:
                dtype = np.dtype(np.object_)
            fill_value = np.nan
        if dtype == np.object_ or dtype.kind in ["U", "S"]:
            fill_value = np.nan
            dtype = np.dtype(np.object_)
    if issubclass(dtype.type, np.datetime64):
        if isinstance(fill_value, datetime) and fill_value.tzinfo is not None:
            dtype = np.dtype(np.object_)
        elif is_integer(fill_value) or (is_float(fill_value) and not isna(fill_value)):
            dtype = np.dtype(np.object_)
        else:
            try:
                fill_value = tslibs.Timestamp(fill_value).to_datetime64()
            except (TypeError, ValueError):
                dtype = np.dtype(np.object_)
    elif issubclass(dtype.type, np.timedelta64):
        if (
            is_integer(fill_value)
            or (is_float(fill_value) and not np.isnan(fill_value))
            or isinstance(fill_value, str)
        ):
            dtype = np.dtype(np.object_)
        else:
            try:
                fv = tslibs.Timedelta(fill_value)
            except ValueError:
                dtype = np.dtype(np.object_)
            else:
                if fv is NaT:
                    fill_value = np.timedelta64("NaT", "ns")
                else:
                    fill_value = fv.to_timedelta64()
    elif is_datetime64tz_dtype(dtype):
        if isna(fill_value):
            fill_value = NaT
    elif is_extension_array_dtype(dtype) and isna(fill_value):
        fill_value = dtype.na_value
    elif is_float(fill_value):
        if issubclass(dtype.type, np.bool_):
            dtype = np.object_
        elif issubclass(dtype.type, np.integer):
            dtype = np.dtype(np.float64)
            if not isna(fill_value):
                fill_value = dtype.type(fill_value)
        elif dtype.kind == "f":
            if not np.can_cast(fill_value, dtype):
                dtype = np.min_scalar_type(fill_value)
        elif dtype.kind == "c":
            if not np.can_cast(fill_value, dtype):
                if np.can_cast(fill_value, np.dtype("c16")):
                    dtype = np.dtype(np.complex128)
                else:
                    dtype = np.dtype(np.object_)
            if dtype.kind == "c" and not np.isnan(fill_value):
                fill_value = dtype.type(fill_value)
    elif is_bool(fill_value):
        if not issubclass(dtype.type, np.bool_):
            dtype = np.object_
        else:
            fill_value = np.bool_(fill_value)
    elif is_integer(fill_value):
        if issubclass(dtype.type, np.bool_):
            dtype = np.dtype(np.object_)
        elif issubclass(dtype.type, np.integer):
            mst = np.min_scalar_type(fill_value)
            if mst > dtype:
                dtype = mst
            elif np.can_cast(fill_value, dtype):
                pass
            elif dtype.kind == "u" and mst.kind == "i":
                dtype = np.promote_types(dtype, mst)
                if dtype.kind == "f":
                    dtype = np.dtype(np.object_)
            elif dtype.kind == "i" and mst.kind == "u":
                if fill_value > np.iinfo(np.int64).max:
                    dtype = np.dtype(np.object_)
                elif mst.itemsize < dtype.itemsize:
                    pass
                elif dtype.itemsize == mst.itemsize:
                    ndt = {
                        np.int64: np.object_,
                        np.int32: np.int64,
                        np.int16: np.int32,
                        np.int8: np.int16,
                    }[dtype.type]
                    dtype = np.dtype(ndt)
                else:
                    ndt = {
                        4: np.int64,
                        2: np.int32,
                        1: np.int16,  
                    }[mst.itemsize]
                    dtype = np.dtype(ndt)
            fill_value = dtype.type(fill_value)
        elif issubclass(dtype.type, np.floating):
            if _check_lossless_cast(fill_value, dtype):
                fill_value = dtype.type(fill_value)
        if dtype.kind in ["c", "f"]:
            fill_value = dtype.type(fill_value)
    elif is_complex(fill_value):
        if issubclass(dtype.type, np.bool_):
            dtype = np.dtype(np.object_)
        elif issubclass(dtype.type, (np.integer, np.floating)):
            c8 = np.dtype(np.complex64)
            info = np.finfo(dtype) if dtype.kind == "f" else np.iinfo(dtype)
            if (
                np.can_cast(fill_value, c8)
                and np.can_cast(info.min, c8)
                and np.can_cast(info.max, c8)
            ):
                dtype = np.dtype(np.complex64)
            else:
                dtype = np.dtype(np.complex128)
        elif dtype.kind == "c":
            mst = np.min_scalar_type(fill_value)
            if mst > dtype and mst.kind == "c":
                dtype = mst
        if dtype.kind == "c":
            fill_value = dtype.type(fill_value)
    elif fill_value is None:
        if is_float_dtype(dtype) or is_complex_dtype(dtype):
            fill_value = np.nan
        elif is_integer_dtype(dtype):
            dtype = np.float64
            fill_value = np.nan
        elif is_datetime_or_timedelta_dtype(dtype):
            fill_value = dtype.type("NaT", "ns")
        else:
            dtype = np.object_
            fill_value = np.nan
    else:
        dtype = np.object_
    if is_extension_array_dtype(dtype):
        pass
    elif issubclass(np.dtype(dtype).type, (bytes, str)):
        dtype = np.object_
    return dtype, fill_value

def retroactive_resolution(
    coefficients, vector
):
    rows, columns = np.shape(coefficients)
    x = np.zeros((rows, 1), dtype=float)
    for row in reversed(range(rows)):
        total = 0
        for col in range(row + 1, columns):
            total += coefficients[row, col] * x[col]
        x[row, 0] = (vector[row] - total) / coefficients[row, row]
    return x

def plot_top_words(model, feature_names, n_top_words, title):
    fig, axes = plt.subplots(2, 5, figsize=(30, 15), sharex=True)
    axes = axes.flatten()
    for topic_idx, topic in enumerate(model.components_):
        top_features_ind = topic.argsort()[: -n_top_words - 1 : -1]
        top_features = [feature_names[i] for i in top_features_ind]
        weights = topic[top_features_ind]
        ax = axes[topic_idx]
        ax.barh(top_features, weights, height=0.7)
        ax.set_title(f"Topic {topic_idx +1}", fontdict={"fontsize": 30})
        ax.invert_yaxis()
        ax.tick_params(axis="both", which="major", labelsize=20)
        for i in "top right left".split():
            ax.spines[i].set_visible(False)
        fig.suptitle(title, fontsize=40)
    plt.subplots_adjust(top=0.90, bottom=0.05, wspace=0.90, hspace=0.3)
    plt.show()

def _fit(self, X):
    if issparse(X):
        raise TypeError(
            "PCA does not support sparse input. See "
            "TruncatedSVD for a possible alternative."
        )
    X = self._validate_data(
        X, dtype=[np.float64, np.float32], ensure_2d=True, copy=self.copy
    )
    if self.n_components is None:
        if self.svd_solver != "arpack":
            n_components = min(X.shape)
        else:
            n_components = min(X.shape) - 1
    else:
        n_components = self.n_components
    self._fit_svd_solver = self.svd_solver
    if self._fit_svd_solver == "auto":
        if max(X.shape) <= 500 or n_components == "mle":
            self._fit_svd_solver = "full"
        elif n_components >= 1 and n_components < 0.8 * min(X.shape):
            self._fit_svd_solver = "randomized"
        else:
            self._fit_svd_solver = "full"
    if self._fit_svd_solver == "full":
        return self._fit_full(X, n_components)
    elif self._fit_svd_solver in ["arpack", "randomized"]:
        return self._fit_truncated(X, n_components, self._fit_svd_solver)
    else:
        raise ValueError(
            "Unrecognized svd_solver='{0}'".format(self._fit_svd_solver)
        )

def _assert_all_finite(
    X, allow_nan=False, msg_dtype=None, estimator_name=None, input_name=""
):
    from .extmath import _safe_accumulator_op
    if _get_config()["assume_finite"]:
        return
    X = np.asanyarray(X)
    is_float = X.dtype.kind in "fc"
    if is_float and (np.isfinite(_safe_accumulator_op(np.sum, X))):
        pass
    elif is_float:
        if (
            allow_nan
            and np.isinf(X).any()
            or not allow_nan
            and not np.isfinite(X).all()
        ):
            if not allow_nan and np.isnan(X).any():
                type_err = "NaN"
            else:
                msg_dtype = msg_dtype if msg_dtype is not None else X.dtype
                type_err = f"infinity or a value too large for {msg_dtype!r}"
            padded_input_name = input_name + " " if input_name else ""
            msg_err = f"Input {padded_input_name}contains {type_err}."
            if (
                not allow_nan
                and estimator_name
                and input_name == "X"
                and np.isnan(X).any()
            ):
                msg_err += (
                    f"\n{estimator_name} does not accept missing values"
                    " encoded as NaN natively. For supervised learning, you might want"
                    " to consider sklearn.ensemble.HistGradientBoostingClassifier and"
                    " Regressor which accept missing values encoded as NaNs natively."
                    " Alternatively, it is possible to preprocess the data, for"
                    " instance by using an imputer transformer in a pipeline or drop"
                    " samples with missing values. See"
                    " https://scikit-learn.org/stable/modules/impute.html"
                    " You can find a list of all estimators that handle NaN values"
                    " at the following page:"
                    " https://scikit-learn.org/stable/modules/impute.html"
                    "#estimators-that-handle-nan-values"
                )
            raise ValueError(msg_err)
    elif X.dtype == np.dtype("object") and not allow_nan:
        if _object_dtype_isnan(X).any():
            raise ValueError("Input contains NaN")

def _fit_stage(self, i, X, y, y_pred, sample_weight, sample_mask,
               random_state, X_idx_sorted, X_csc=None, X_csr=None):
    assert sample_mask.dtype == np.bool
    loss = self.loss_
    original_y = y
    for k in range(loss.K):
        if loss.is_multi_class:
            y = np.array(original_y == k, dtype=np.float64)
        residual = loss.negative_gradient(y, y_pred, k=k,
                                          sample_weight=sample_weight)
        tree = DecisionTreeRegressor(
            criterion=self.criterion,
            splitter='best',
            max_depth=self.max_depth,
            min_samples_split=self.min_samples_split,
            min_samples_leaf=self.min_samples_leaf,
            min_weight_fraction_leaf=self.min_weight_fraction_leaf,
            min_impurity_decrease=self.min_impurity_decrease,
            min_impurity_split=self.min_impurity_split,
            max_features=self.max_features,
            max_leaf_nodes=self.max_leaf_nodes,
            random_state=random_state,
            presort=self.presort)
        if self.subsample < 1.0:
            sample_weight = sample_weight * sample_mask.astype(np.float64)
        if X_csc is not None:
            tree.fit(X_csc, residual, sample_weight=sample_weight,
                     check_input=False, X_idx_sorted=X_idx_sorted)
        else:
            tree.fit(X, residual, sample_weight=sample_weight,
                     check_input=False, X_idx_sorted=X_idx_sorted)
        if X_csr is not None:
            loss.update_terminal_regions(tree.tree_, X_csr, y, residual, y_pred,
                                         sample_weight, sample_mask,
                                         self.learning_rate, k=k)
        else:
            loss.update_terminal_regions(tree.tree_, X, y, residual, y_pred,
                                         sample_weight, sample_mask,
                                         self.learning_rate, k=k)
        self.estimators_[i, k] = tree
    return y_pred

def _mini_batch_step(X, x_squared_norms, centers, counts,
                     old_center_buffer, compute_squared_diff,
                     distances, random_reassign=False,
                     random_state=None, reassignment_ratio=.01,
                     verbose=False):
    nearest_center, inertia = _labels_inertia(X, x_squared_norms, centers,
                                              distances=distances)
    if random_reassign and reassignment_ratio > 0:
        random_state = check_random_state(random_state)
        to_reassign = np.logical_or(
            (counts <= 1), counts <= reassignment_ratio * counts.max())
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
    k = centers.shape[0]
    squared_diff = 0.0
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
                squared_diff += np.sum(
                    (centers[center_idx] - old_center_buffer) ** 2)
    return inertia, squared_diff

def pairwise_distances_argmin_min(X, Y, axis=1, metric="euclidean",
                                  batch_size=500, metric_kwargs={}):
    dist_func = None
    if metric in PAIRWISE_DISTANCE_FUNCTIONS:
        dist_func = PAIRWISE_DISTANCE_FUNCTIONS[metric]
    elif not callable(metric) and not isinstance(metric, str):
        raise ValueError("'metric' must be a string or a callable")
    X, Y = check_pairwise_arrays(X, Y)
    if axis == 0:
        X, Y = Y, X
    indices = np.empty(X.shape[0], dtype='int32')
    values = np.empty(X.shape[0])
    values.fill(np.infty)
    for chunk_x in gen_batches(X.shape[0], batch_size):
        X_chunk = X[chunk_x, :]
        for chunk_y in gen_batches(Y.shape[0], batch_size):
            Y_chunk = Y[chunk_y, :]
            if dist_func is not None:
                if metric == 'euclidean':  
                    dist_chunk = np.dot(X_chunk, Y_chunk.T)
                    dist_chunk *= -2
                    dist_chunk += (X_chunk * X_chunk
                                   ).sum(axis=1)[:, np.newaxis]
                    dist_chunk += (Y_chunk * Y_chunk
                                   ).sum(axis=1)[np.newaxis, :]
                    np.maximum(dist_chunk, 0, dist_chunk)
                else:
                    dist_chunk = dist_func(X_chunk, Y_chunk, **metric_kwargs)
            else:
                dist_chunk = pairwise_distances(X_chunk, Y_chunk,
                                                metric=metric, **metric_kwargs)
            min_indices = dist_chunk.argmin(axis=1)
            min_values = dist_chunk[range(chunk_x.stop - chunk_x.start),
                                    min_indices]
            flags = values[chunk_x] > min_values
            indices[chunk_x] = np.where(
                flags, min_indices + chunk_y.start, indices[chunk_x])
            values[chunk_x] = np.where(
                flags, min_values, values[chunk_x])
    if metric == "euclidean" and not metric_kwargs.get("squared", False):
        values = np.sqrt(values)
    return indices, values

def set_spidercls(self, url, opts):
    spider_loader = self.crawler_process.spider_loader
    if opts.spider:
        try:
            self.spidercls = spider_loader.load(opts.spider)
        except KeyError:
            logger.error('Unable to find spider: %(spider)s',
                         {'spider': opts.spider})
    else:
        self.spidercls = spidercls_for_request(spider_loader, Request(url))
        if not self.spidercls:
            logger.error('Unable to find spider for: %(url)s', {'url': url})
    def _start_requests(spider):
        yield self.prepare_request(spider, Request(url, None), opts)
    self.spidercls.start_requests = _start_requests

def add_cookie_header(self, request):
    wreq = WrappedRequest(request)
    self.policy._now = self.jar._now = int(time.time())
    req_host = urlparse_cached(request).hostname
    if not req_host:
        return
    if not IPV4_RE.search(req_host):
        hosts = potential_domain_matches(req_host)
        if req_host.find(".") == -1:
            hosts += [req_host + ".local"]
    else:
        hosts = [req_host]
    cookies = []
    for host in hosts:
        if host in self.jar._cookies:
            cookies += self.jar._cookies_for_domain(host, wreq)
    attrs = self.jar._cookie_attrs(cookies)
    if attrs:
        if not wreq.has_header("Cookie"):
            wreq.add_unredirected_header("Cookie", "; ".join(attrs))
    self.processed += 1
    if self.processed % self.check_expired_frequency == 0:
        self.jar.clear_expired_cookies()

def _requests_to_follow(self, response):
    seen = set()
    for n, rule in enumerate(self._rules):
        links = [l for l in rule.link_extractor.extract_links(response) if l not in seen]
        if links and rule.process_links:
            links = rule.process_links(links)
        seen = seen.union(links)
        for link in links:
            r = Request(url=link.url, callback='_response_downloaded')
            r.meta.update(rule=n, link_text=link.text)
            yield rule.process_request(r)

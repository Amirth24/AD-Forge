-- Initial schema for solution-architect-spl

CREATE TABLE IF NOT EXISTS problems (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    tags TEXT NOT NULL DEFAULT '[]',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS solutions (
    id TEXT PRIMARY KEY,
    problem_id TEXT NOT NULL,
    title TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'draft',
    body TEXT NOT NULL DEFAULT '',
    comments TEXT NOT NULL DEFAULT '[]',
    reviews TEXT NOT NULL DEFAULT '[]',
    labels TEXT NOT NULL DEFAULT '[]',
    assignees TEXT NOT NULL DEFAULT '[]',
    cost_summary TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (problem_id) REFERENCES problems(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_solutions_problem_id ON solutions(problem_id);

CREATE TABLE IF NOT EXISTS sub_problems (
    id TEXT PRIMARY KEY,
    problem_id TEXT NOT NULL,
    solution_id TEXT,
    parent_id TEXT,
    title TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    tags TEXT NOT NULL DEFAULT '[]',
    complexity INTEGER NOT NULL DEFAULT 3,
    status TEXT NOT NULL DEFAULT 'draft',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (problem_id) REFERENCES problems(id) ON DELETE CASCADE,
    FOREIGN KEY (solution_id) REFERENCES solutions(id) ON DELETE SET NULL,
    FOREIGN KEY (parent_id) REFERENCES sub_problems(id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS idx_sub_problems_problem_id ON sub_problems(problem_id);
CREATE INDEX IF NOT EXISTS idx_sub_problems_solution_id ON sub_problems(solution_id);

CREATE TABLE IF NOT EXISTS solution_nodes (
    id TEXT PRIMARY KEY,
    solution_id TEXT NOT NULL,
    sub_problem_id TEXT,
    node_type TEXT NOT NULL DEFAULT 'sub_problem',
    title TEXT NOT NULL DEFAULT '',
    description TEXT NOT NULL DEFAULT '',
    data TEXT NOT NULL DEFAULT '{}',
    FOREIGN KEY (solution_id) REFERENCES solutions(id) ON DELETE CASCADE,
    FOREIGN KEY (sub_problem_id) REFERENCES sub_problems(id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS idx_solution_nodes_solution_id ON solution_nodes(solution_id);

CREATE TABLE IF NOT EXISTS solution_edges (
    id TEXT PRIMARY KEY,
    solution_id TEXT NOT NULL,
    from_node_id TEXT NOT NULL,
    to_node_id TEXT NOT NULL,
    edge_type TEXT NOT NULL DEFAULT 'depends_on',
    data TEXT NOT NULL DEFAULT '{}',
    FOREIGN KEY (solution_id) REFERENCES solutions(id) ON DELETE CASCADE,
    FOREIGN KEY (from_node_id) REFERENCES solution_nodes(id) ON DELETE CASCADE,
    FOREIGN KEY (to_node_id) REFERENCES solution_nodes(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_solution_edges_solution_id ON solution_edges(solution_id);

CREATE TABLE IF NOT EXISTS cost_line_items (
    id TEXT PRIMARY KEY,
    solution_id TEXT NOT NULL,
    sub_problem_id TEXT,
    provider TEXT NOT NULL,
    service TEXT NOT NULL,
    region TEXT NOT NULL DEFAULT '',
    parameters TEXT NOT NULL DEFAULT '{}',
    unit_price TEXT NOT NULL,
    quantity TEXT NOT NULL DEFAULT '1',
    unit TEXT NOT NULL DEFAULT '',
    source_url TEXT NOT NULL DEFAULT '',
    source_fetched_at TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (solution_id) REFERENCES solutions(id) ON DELETE CASCADE,
    FOREIGN KEY (sub_problem_id) REFERENCES sub_problems(id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS idx_cost_line_items_solution_id ON cost_line_items(solution_id);

CREATE TABLE IF NOT EXISTS pricing_cache (
    key TEXT PRIMARY KEY,
    provider TEXT NOT NULL,
    service TEXT NOT NULL,
    region TEXT NOT NULL DEFAULT '',
    parameters_hash TEXT NOT NULL DEFAULT '',
    response TEXT NOT NULL,
    fetched_at TEXT NOT NULL,
    expires_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_pricing_cache_expires ON pricing_cache(expires_at);

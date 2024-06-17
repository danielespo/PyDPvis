def dpll(clauses, assignment=[]):
    if not clauses:
        return assignment
    if any([c == [] for c in clauses]):
        return False
    
    for clause in clauses:
        if len(clause) == 1:
            l = clause[0]
            new_clauses = [c for c in clauses if l not in c]
            new_clauses = [list(filter(lambda x: x != -l, c)) for c in new_clauses]
            return dpll(new_clauses, assignment + [l])
    
    l = clauses[0][0]
    new_clauses = [c for c in clauses if l not in c]
    new_clauses = [list(filter(lambda x: x != -l, c)) for c in new_clauses]
    return dpll(new_clauses, assignment + [l]) or dpll(clauses, assignment + [-l])

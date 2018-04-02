"""
SAT solver using CDCL
"""
from .constants import DEFAULT_FILE, TRUE, FALSE, UNASSIGN
from .exceptions import FileFomratError
from .logger import set_logger

logger = set_logger()


class Solver:

    def __init__(self, filename=DEFAULT_FILE):
        self.filename = filename
        self.cnf, self.vars = Solver.read_file(filename)
        self.assignments = dict.fromkeys(list(self.vars), UNASSIGN)

    def solve(self):
        pass

    @staticmethod
    def read_file(filename):
        """
        Reads a DIMACS CNF format file, returns clauses (set of frozenset) and
        literals (set of int).
            :param filename: the file name
            :raises FileFormatError: when file format is wrong
            :returns: (clauses, literals)
        """
        with open(filename) as f:
            lines = [
                line.strip().split(' ') for line in f.readlines()
                if not line.startswith('c') and line != '\n'
            ]

        if lines[0][:2] == ['p', 'cnf']:
            count_literals, count_clauses = map(int, lines[0][-2:])
        else:
            raise FileFomratError('Number of literals and clauses are not declared properly.')

        literals = set()
        clauses = set()

        for line in lines[1:]:
            if line[-1] != '0':
                raise FileFomratError('Each line of clauses must end with 0.')
            clause = frozenset(map(int, line[:-1]))
            literals.update(map(abs, clause))
            clauses.add(clause)

        if len(literals) != count_literals or len(clauses) != count_clauses:
            raise FileFomratError('Unmatched literal count or clause count.')

        logger.fine('clauses: %s', clauses)
        logger.fine('literals: %s', literals)

        return clauses, literals

    @staticmethod
    def compute_value(literal, assignment):
        """
        Compute the value of the literal (could be -/ve or +/ve) from
        `assignment`. Returns -1 if unassigned
            :param literal: an int, can't be 0
            :param assignment: a dictionary mapping int -> 0 | 1
            :returns: value of the literal
        """
        logger.finest('literal: %s', literal)
        logger.finest('assignment: %s', assignment)
        if literal == 0:
            raise ValueError('0 is an invalid literal!')

        variable = abs(literal)
        if variable not in assignment:
            logger.finest('%s not in assignment', variable)
            return UNASSIGN
        value = assignment[variable] ^ (literal < 0)
        logger.finest('value: %s', value)
        return value

    @staticmethod
    def compute_clause(clause, assignment):
        logger.finer('clause: %s', clause)
        logger.finer('assignment: %s', assignment)
        return max([Solver.compute_value(literal, assignment) for literal in clause])

    def compute_cnf(self):
        logger.debug('cnf: %s', self.cnf)
        logger.debug('assignments: %s', self.assignments)
        return min([Solver.compute_clause(clause, self.assignments) for clause in self.cnf])

    @staticmethod
    def is_unit_clause(clause, assignment):
        """
        Checks if clause is a unit clause. If and only if there is
        exactly 1 literal unassigned, and all the other literals having
        value of 0.
            :param clause: set of ints
            :param assignment: a dictionary mapping int -> 0 | 1
            :returns: (is_clause_a_unit, the_literal)
        """
        logger.finer('assignment: %s', assignment)

        values = []
        unassigned = None

        for literal in clause:
            value = Solver.compute_value(literal, assignment)
            values.append(value)
            unassigned = literal if value == UNASSIGN else None

        check = (values.count(FALSE) == len(clause) - 1 and
                 values.count(UNASSIGN) == 1)
        logger.fine('%s: %s', clause, (check, unassigned))
        return check, unassigned

    @staticmethod
    def unit_propagate(clauses, assignment):
        """
        A unit clause has all of its literals but 1 assigned to 0. Then, the sole
        unassigned literal must be assigned to value 1. Unit propagation is the
        process of iteratively applying the unit clause rule.
            :param clauses: set of sets of int
            :param assignment: a dictionary mapping int -> 0 | 1
            :returns: the resultant assignment
        """
        # for clause in clauses:
        # flag, literal = is_unit_clause(clause, assignment)
        # if flag:
        # assignment[literal] = 1

        pass

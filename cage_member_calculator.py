

def get_cage_members(N, target_total):
    def find_n_numbers_sum_to_target(A, target_sum, selecteds, N, target_set):
        for i in range(0, len(A)):
            selecteds.append(A.pop())
            if len(selecteds) == N:
                if sum(selecteds) == target_sum:
                    print("%s numbers are %s" % (N, selecteds))
                    target_set.union(set(selecteds))
            else:
                find_n_numbers_sum_to_target(list(A), target_sum, selecteds, N, target_set)
            selecteds.pop()

    candidates = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    candidates.sort(reverse=True)
    target_set = set([])
    selecteds = []
    find_n_numbers_sum_to_target(candidates, target_total, selecteds, N, target_set)
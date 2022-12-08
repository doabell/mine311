class cspsolver():
    #     domains
    #     neighbors=[]

    deletedconstraints = []
    oldfreecells = set()
    newfreecells = set()
    g.click((5, 5))  # first click at (0,0)
    newfreecells = g.revealed

    def addconstraints(self):
        nonlocal constraints
        for cell in g.revealed:
            if g.vboard[cell[0]][cell[1]] != 0:
                if (cell not in constraints.keys()) and (cell not in deletedconstraints):
                    unknownneighs = set()
                    for i in range(cell[0] - 1, cell[0] + 2):
                        for j in range(cell[1] - 1, cell[1] + 2):
                            if (i, j) == cell:
                                continue
                            if 0 <= i < g.height and 0 <= j < g.width:
                                if g.vboard[i][j] == -2:
                                    unknownneighs.add((i, j))
                    constraints[cell] = [unknownneighs,
                                         g.vboard[cell[0]][cell[1]]]
                    # decrement #mines by counts of flagged unkonwnneighs
                    for i in range(cell[0] - 1, cell[0] + 2):
                        # i,j  potential flagged cell
                        for j in range(cell[1] - 1, cell[1] + 2):
                            if (i, j) == cell:
                                continue
                            if 0 <= i < g.height and 0 <= j < g.width:
                                if g.vboard[i][j] == -3:
                                    constraints[cell][1] = constraints[cell][1]-1
        return None

    def pruneunknownneighs():
        nonlocal constraints
        for constraint in constraints:
            unknownneighscopy = constraints[constraint][0].copy()
            for unknownneigh in unknownneighscopy:
                for newfreecell in newfreecells:
                    if unknownneigh == newfreecell:
                        constraints[constraint][0].remove(unknownneigh)
        return None

    def trivialflag():  # add to toflag, delete constraints, modify remaining constraints
        nonlocal toflag, self.to_click, constraints
#         constodelete:list[tuple]=[]
        constraintscopy = copy.deepcopy(constraints)
        for constraint in constraintscopy:
            if len(constraints[constraint][0]) == constraints[constraint][1]:
                # base case
                if len(constraints[constraint][0]) == 0 and constraints[constraint][1] == 0:
                    constraints.pop(constraint)  # not in constraints anymore!
                else:
                    minescopy = constraints[constraint][0].copy()
    #                 print('len of before constrs ',len(constraints))
                    deletedconstraints.append(constraint)
                    constraints.pop(constraint)
#                     print('deleted(constraints with amn, toflag())',deletedconstraints)
    #                 print('len of after constraints ',len(constraints))
                    for mine in minescopy:
                        toflag.append(mine)
#                         print('toflag(added a new mine) ',toflag)
                        # (i,j)s are neighs of mine; if neighs are constraints movidfy neighs of flagge mine
                        for i in range(mine[0] - 1, mine[0] + 2):
                            for j in range(mine[1] - 1, mine[1] + 2):
                                if (i, j) == mine:
                                    continue
                                if 0 <= i < g.height and 0 <= j < g.width:
                                    if (i, j) in constraints.keys() and len(constraints[(i, j)][0]) != 0:
                                        #                                         print('mine ',mine, 'constraint with m',(i,j), ' ',constraints[(i,j)])
                                        constraints[(i, j)][0].remove(mine)
    #                                     newminecount=constraints[(i,j)][1]
                                        constraints[(i, j)][1] = constraints[(
                                            i, j)][1]-1
#                                         print('constraint with m',(i,j),'after remove m ',constraints[(i,j)])
        constraintscp2 = copy.deepcopy(constraints)
# #         print(constraint ,' ', constraints[constraint])
        for constraint in constraintscp2:  # remove constraint with no cell and score 0
            if constraints[constraint][1] == 0:  # all unknownneighs are free, afn
                trivialclick()
                break
            # this unknownneigh is mine,amn
            elif len(constraints[constraint][0]) == constraints[constraint][1]:
                trivialflag()
                break
        return None

    def trivialclick():
        nonlocal toflag, self.to_click, constraints
        constraintscopy = copy.deepcopy(constraints)
        for constraint in constraintscopy:
            if constraints[constraint][1] == 0:
                # base case
                if len(constraints[constraint][0]) == 0 and constraints[constraint][1] == 0:
                    constraints.pop(constraint)
                else:
                    freescopy = constraints[constraint][0].copy()
                    deletedconstraints.append(constraint)
                    constraints.pop(constraint)
#                     print('deleted(constraint with afn,toclick()) ',deletedconstraints)
                    for free in freescopy:
                        self.to_click.append(free)
#                         print('toclick(added a new free) ',toclick)
                        # (i,j)s are neighs of free that initially contained free; remove all instances of free from lists of unknownneighs of all constraints
                        for i in range(free[0] - 1, free[0] + 2):
                            for j in range(free[1] - 1, free[1] + 2):
                                if (i, j) == free:
                                    continue
                                if 0 <= i < g.height and 0 <= j < g.width:
                                    if (i, j) in constraints.keys():
                                        #                                         print('free ',free, 'constraint with f',(i,j), ' ',constraints[(i,j)])
                                        constraints[(i, j)][0].remove(free)
#                                         print('constraint with f',(i,j),'after remove f ',constraints[(i,j)])
        constraintscp2 = copy.deepcopy(constraints)
        for constraint in constraintscp2:  # remove constraint with no cell and score 0
            if constraints[constraint][1] == 0:  # all unknownneighs are free
                trivialclick()
                break
            # this unknownneigh is mine
            elif len(constraints[constraint][0]) == constraints[constraint][1]:
                trivialflag()
                break

        return None

    def constraintsreduction():
        nonlocal toflag, self.to_click, constraints
#         print('g.mines ',g.mines)
        constraintscopy = copy.deepcopy(constraints)
        for c1 in constraintscopy:  # looping cpy, modifying constraints
            for c2 in constraintscopy:
                if (c1 != c2) and (c1 in constraints.keys()) and (c2 in constraints.keys()):
                    if constraints[c1][1] == constraints[c2][1] and constraints[c1][0] != constraints[c2][0]:
                        #                         print('c1 ',c1,constraints[c1],'c2',c2,constraints[c2])
                        # and len(constraints[c1][0])<len(constraints[c2][0]):
                        if constraints[c1][0].issubset(constraints[c2][0]):
                            #                             print('c1 ',c1,constraints[c1],'c2',c2,constraints[c2])
                            frees = (constraints[c2][0] -
                                     constraints[c1][0]).copy()
                            for free in frees:
                                self.to_click.append(free)
                                # (i,j)s are neighs of free; remove all instances of free from list unknown in all constraints
                                for i in range(free[0] - 1, free[0] + 2):
                                    for j in range(free[1] - 1, free[1] + 2):
                                        if (i, j) == free:
                                            continue
                                        if 0 <= i < g.height and 0 <= j < g.width:
                                            if (i, j) in constraints.keys():
                                                #                                                 print('(r)free',free, 'constraint with f',(i,j), ' ',constraints[(i,j)])
                                                constraints[(i, j)][0].remove(
                                                    free)
#                                                 print('(r)constraint with f',(i,j),'after remove f ',constraints[(i,j)])
                        # and len(constraints[c2][0])<len(constraints[c1][0]):
                        elif constraints[c2][0].issubset(constraints[c1][0]):
                            #                             print('c1 ',c1,constraints[c1],'c2',c2,constraints[c2])
                            frees = constraints[c1][0]-constraints[c2][0]
                            for free in frees:
                                self.to_click.append(free)
                                # (i,j)s are neighs of free; remove all instances of free from list unknown in all constraints
                                for i in range(free[0] - 1, free[0] + 2):
                                    for j in range(free[1] - 1, free[1] + 2):
                                        if (i, j) == free:
                                            continue
                                        if 0 <= i < g.height and 0 <= j < g.width:
                                            if (i, j) in constraints.keys():
                                                #                                                 print('(r)free',free, 'constraint with f',(i,j), ' ',constraints[(i,j)])
                                                constraints[(i, j)][0].remove(
                                                    free)
#                                                 print('(r)constraint with f',(i,j),'after remove f ',constraints[(i,j)])

        trivialflag()
        constraintscpy2 = copy.deepcopy(constraints)
        for c1 in constraintscpy2:
            for c2 in constraintscpy2:
                if (c1 != c2) and (c1 in constraints.keys()) and (c2 in constraints.keys()):
                    if (constraints[c1][1] == constraints[c2][1]) and (constraints[c1][0] != constraints[c2][0]):
                        if constraints[c1][0].issubset(constraints[c2][0]) or constraints[c2][0].issubset(constraints[c1][0]):
                            constraintsreduction()
                            break
        return None
#     print('mines ',g.mines)
    while g.outcome() is None:
        #         print('oldfreecells ',oldfreecells)
        newfreecells = g.revealed.difference(oldfreecells)
#         print("allfreecells ", g.revealed)
#         print("allfreecells-oldfreecells ",newfreecells)
        pruneunknownneighs()
#         print('g.flags: ',g.flags)
#         print('g.revealed ', g.revealed)
#         print('g.vboard below: ')
#         for row in g.vboard:
#             print(row)
#         print ('constraints ',constraints)
#         print('toclick: ',toclick)
#         print('toflag ',toflag)
        if len(self.to_click) != 0:
            #             print('cell to click ',toclick[0])
            oldfreecells = g.revealed.copy()
            g.click(self.to_click[0])
            self.to_click.remove(self.to_click[0])
        elif len(self.to_flag) != 0:
            #             print('cell to flag ',toflag[0])
            oldfreecells = g.revealed.copy()
            g.flag(self.to_flag[0])
            self.to_flag.remove(self.to_flag[0])
        else:
            addconstraints()
#             print('consts after addconsts()', constraints)
            trivialflag()
#             print('constraints before r ',constraints)
            constraintsreduction()
#             print ('constraints after r',constraints)
#             print('toclick ',toclick)
#             print('toflag ',toflag)
            if len(self.to_click) != 0:
                #                 print('cell to click ',toclick[0])
                oldfreecells = g.revealed.copy()
                g.click(self.to_click[0])
                self.to_click.remove(self.to_click[0])
            elif len(self.to_flag) != 0:
                #                 print('cell to flag ',toflag[0])
                oldfreecells = g.revealed.copy()
                g.flag(self.to_flag[0])
                self.to_flag.remove(self.to_flag[0])
            else:
                for constraint in self.constraints:
                    unknownneighs = self.constraints[constraint][0]
                    for unknownneigh in unknownneighs:
                        if unknownneigh not in g.revealed:
                            oldfreecells = g.revealed.copy()
#                             print('oldfreecells ',oldfreecells)
#                             print('unkonwnneigh choice ',unknownneigh)
                            g.click(unknownneigh)
                            break
                    break
#     if !game.outcome():
    return g.outcome()

comment1 = """#
#   $Id$
#
#   $Log$

#
#   DMAN V2 runlist
#

#
# batch control items --------------------
#"""

comment2 = """# cathode wheel list items --------------------
#
#   v-- cathode position in wheel (key)
#   v    v-- sample type
#   v    v        v-- sample name
#   v    v        v                v-- sample name 2
#   4    8        16               16
#   Pos  SmType   Sample Name      Sample Name 2
#   ==== ======== ================ ================"""

comment3 = """#
# run list items --------------------
#    v-- item (key)
#    v    v-- position (cathode position in wheel)
#    v    v    v-- group
#    v    v    v   v-- summary group
#    v    v    v   v   v-- number of measurements to perform
#    v    v    v   v   v    v-- mode time/counts(T/C)
#    v    v    v   v   v    v  v-- # of cycles in measurement
#    v    v    v   v   v    v  v      v-- # max number of events when mode=C
#    v    v    v   v   v    v  v      v      v-- warmup time in cycles
#    v    v    v   v   v    v  v      v      v    v-- minimum runs to judge
#    v    v    v   v   v    v  v      v      v    v  v-- judgement error limit
#    v    v    v   v   v    v  v      v      v    v  v
#    4    4    6   3   4    2  6      6      4    2  6
#    Item Pos  Grp Sum Runs Md Tlimit Climit Warm Jn Jlimit
#    ==== ==== === === ==== == ====== ====== ==== == ======"""

comment4 = """#
#   Summary definitions
#
#   v-- group number
#   v   v-- group name
#   3   16
#   Grp Group Name
#   === ================"""

if __name__ == '__main__':
    print(comment1)
    print(comment2)
    print(comment3)
    print(comment4)
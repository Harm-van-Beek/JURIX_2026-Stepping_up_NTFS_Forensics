# We define initial NTFS timestamp structures excluding and including file tunneling. 
# There are 12 initial NTFS timestamp structures excluding initial strucutures due to file tunneling.
# There are 16 initial NTFS timestamp strucutures including initial strucutures due to file tunneling.

# ==============================================================================
# Initial NTFS timestamp strucutures excluding file tunneling
# ==============================================================================

# ------------------------------------------------------------------------------
# 1. Create (CR)
# ------------------------------------------------------------------------------

# CR: si_1 = si_2 = si_3 = si_4 = fn_1 = fn_2 = fn_3 = fn_4
CR = "leq(0,X,Y):- timestamp(X), timestamp(Y)."

ntfs_initial_TS_CR = [CR]

# ------------------------------------------------------------------------------
# 2. Copy (CO)
# ------------------------------------------------------------------------------

# CO: si_2 <= si_1 = si_4 = fn_1 = fn_2 = fn_3 = fn_4 <= si_3

# CO_1: si_1 = si_2 = si_4 = fn_1 = fn_2 = fn_3 = fn_4 = si_3
CO_1 = "leq(0,X,Y):- timestamp(X), timestamp(Y)."
# CO_2: si_2 < si_1 = si_4 = fn_1 = fn_2 = fn_3 = fn_4 = si_3
CO_2 = "leq(0,X,X) :-   timestamp(X). leq(0,X,Y) :-   timestamp(X), timestamp(Y), Y != si_2."
# CO_3: si_1 = si_2 = si_4 = fn_1 = fn_2 = fn_3 = fn_4 < si_3
CO_3 = "leq(0,X,X) :-   timestamp(X). leq(0,X,Y) :-   timestamp(X), timestamp(Y), X != si_3."
# CO_4: si_2 < si_1 = si_4 = fn_1 = fn_2 = fn_3 = fn_4 < si_3
CO_4 = "leq(0,X,X) :-   timestamp(X). leq(0,X,Y) :-   timestamp(X), timestamp(Y), X != si_3, Y != si_2."


# ------------------------------------------------------------------------------
# # 3.Move from other volume (MV)
# ------------------------------------------------------------------------------

# MV: si_1 <= si_2 <= si_4 = fn_1 = fn_2 = fn_3 = fn_4 <= si_3 
# or  si_2 <= si_1 <= si_4 = fn_1 = fn_2 = fn_3 = fn_4 <= si_3

#Case 1: si_1 <= si_2 <= si_4 = fn_1 = fn_2 = fn_3 = fn_4 <= si_3 

# MV_11: si_1 = si_2 = si_4 = fn_1 = fn_2 = fn_3 = fn_4 = si_3
MV_11 = "leq(0,X,Y):- timestamp(X), timestamp(Y)."
# MV_12: si_1 < si_2 = si_4 = fn_1 = fn_2 = fn_3 = fn_4 = si_3
MV_12 = "leq(0,X,X) :-   timestamp(X). leq(0,X,Y) :-   timestamp(X), timestamp(Y), Y != si_1."

# MV_13: si_1 = si_2 < si_4 = fn_1 = fn_2 = fn_3 = fn_4 = si_3
MV_13 = "leq(0,X,X) :-   timestamp(X). leq(0,X,Y) :-   timestamp(X), timestamp(Y), Y != si_1, Y != si_2. leq(0,si_1,si_2). leq(0,si_2,si_1)."
# MV_14: si_1 < si_2 < si_4 = fn_1 = fn_2 = fn_3 = fn_4 = si_3
MV_14 = "leq(0,X,X) :-   timestamp(X). leq(0,X,Y) :-   timestamp(X), timestamp(Y), Y != si_1, Y != si_2. leq(0,si_1,si_2)."

# MV_15: si_1 = si_2 = si_4 = fn_1 = fn_2 = fn_3 = fn_4 < si_3
MV_15 = "leq(0,X,X) :-   timestamp(X). leq(0,X,Y) :-   timestamp(X), timestamp(Y), X != si_3."
# MV_16: si_1 < si_2 = si_4 = fn_1 = fn_2 = fn_3 = fn_4 < si_3
MV_16 = "leq(0,X,X) :-   timestamp(X). leq(0,X,Y) :-   timestamp(X), timestamp(Y), X != si_3, Y != si_1."

# MV_17: si_1 = si_2 < si_4 = fn_1 = fn_2 = fn_3 = fn_4 < si_3
MV_17 = "leq(0,X,X) :-   timestamp(X). leq(0,X,Y) :-   timestamp(X), timestamp(Y), X != si_3, Y != si_1, Y != si_2. leq(0,si_1,si_2).leq(0,si_2,si_1)."
# MV_18: si_1 < si_2 < si_4 = fn_1 = fn_2 = fn_3 = fn_4 < si_3
MV_18 = "leq(0,X,X) :-   timestamp(X). leq(0,X,Y) :-   timestamp(X), timestamp(Y), X != si_3, Y != si_1, Y != si_2. leq(0,si_1,si_2)."

#Case 2: si_2 <= si_1 <= si_4 = fn_1 = fn_2 = fn_3 = fn_4 <= si_3 

# MV_21: si_2 = si_1 = si_4 = fn_1 = fn_2 = fn_3 = fn_4 = si_3
MV_21 = "leq(0,X,Y):- timestamp(X), timestamp(Y)."
# MV_22: si_2 < si_1 = si_4 = fn_1 = fn_2 = fn_3 = fn_4 = si_3
MV_22 = "leq(0,X,X) :-   timestamp(X). leq(0,X,Y) :-   timestamp(X), timestamp(Y), Y != si_2."

# MV_23: si_2 = si_1 < si_4 = fn_1 = fn_2 = fn_3 = fn_4 = si_3
MV_23 = "leq(0,X,X) :-   timestamp(X). leq(0,X,Y) :-   timestamp(X), timestamp(Y), Y != si_1, Y != si_2. leq(0,si_1,si_2). leq(0,si_2,si_1)."
# MV_24: si_2 < si_1 < si_4 = fn_1 = fn_2 = fn_3 = fn_4 = si_3
MV_24 = "leq(0,X,X) :-   timestamp(X). leq(0,X,Y) :-   timestamp(X), timestamp(Y), Y != si_1, Y != si_2. leq(0,si_2,si_1)."

# MV_25: si_2 = si_1 = si_4 = fn_1 = fn_2 = fn_3 = fn_4 < si_3
MV_25 = "leq(0,X,X) :-   timestamp(X). leq(0,X,Y) :-   timestamp(X), timestamp(Y), X != si_3."
# MV_26: si_2 < si_1 = si_4 = fn_1 = fn_2 = fn_3 = fn_4 < si_3
MV_26 = "leq(0,X,X) :-   timestamp(X). leq(0,X,Y) :-   timestamp(X), timestamp(Y), X != si_3, Y != si_2."

# MV_27: si_2 = si_1 < si_4 = fn_1 = fn_2 = fn_3 = fn_4 < si_3
MV_27 = "leq(0,X,X) :-   timestamp(X). leq(0,X,Y) :-   timestamp(X), timestamp(Y), X != si_3, Y != si_1, Y != si_2. leq(0,si_1,si_2).leq(0,si_2,si_1)."
# MV_28: si_2 < si_1 < si_4 = fn_1 = fn_2 = fn_3 = fn_4 < si_3
MV_28 = "leq(0,X,X) :-   timestamp(X). leq(0,X,Y) :-   timestamp(X), timestamp(Y), X != si_3, Y != si_1, Y != si_2. leq(0,si_2,si_1)."


# ==============================================================================
# List of initial NTFS timestamp strucutures without file tunneling
# ==============================================================================

ntfs_initial_TS = list({CR, 
                        CO_1, CO_2, CO_3, CO_4, 
                        MV_11, MV_12, MV_13, MV_14, MV_15, MV_16, MV_17, MV_18,
                        MV_21, MV_22, MV_23, MV_24, MV_25, MV_26, MV_27, MV_28})



# ==============================================================================
# Initial NTFS timestamp strucutures due to file tunneling
# ==============================================================================

# FT: si_1 <= fn_1 <= si_2 = si_3 = si_4 = fn_2 = fn_3 = fn_4
# or  fn_1 <= si_1 <= si_2 = si_3 = si_4 = fn_2 = fn_3 = fn_4

# Case 1: si_1 <= fn_1 <= si_2 = si_3 = si_4 = fn_2 = fn_3 = fn_4

# FT_11: si_1 = fn_1 = si_2 = si_3 = si_4 = fn_2 = fn_3 = fn_4
FT_11 = "leq(0,X,Y):- timestamp(X), timestamp(Y)."
# FT_12: si_1 = fn_1 < si_2 = si_3 = si_4 = fn_2 = fn_3 = fn_4
FT_12 = "leq(0,X,X) :-   timestamp(X). leq(0,X,Y) :-   timestamp(X), timestamp(Y), Y != si_1, Y != fn_1. leq(0,si_1, fn_1). leq(0,fn_1, si_1)."

# FT_13: si_1 < fn_1 = si_2 = si_3 = si_4 = fn_2 = fn_3 = fn_4
FT_13 = "leq(0,X,X) :-   timestamp(X). leq(0,X,Y) :-   timestamp(X), timestamp(Y), Y != si_1."
# FT_14: si_1 < fn_1 < si_2 = si_3 = si_4 = fn_2 = fn_3 = fn_4
FT_14 = "leq(0,X,X) :-   timestamp(X). leq(0,X,Y) :-   timestamp(X), timestamp(Y), Y != si_1, Y != fn_1. leq(0, si_1, fn_1)."

# Case 2: fn_1 <= si_1 <= si_2 = si_3 = si_4 = fn_2 = fn_3 = fn_4

# FT_21: fn_1 = si_1 = si_2 = si_3 = si_4 = fn_2 = fn_3 = fn_4
FT_21 = "leq(0,X,Y):- timestamp(X), timestamp(Y)."
# FT_22: fn_1 = si_1 < si_2 = si_3 = si_4 = fn_2 = fn_3 = fn_4
FT_22 = "leq(0,X,X) :-   timestamp(X). leq(0,X,Y) :-   timestamp(X), timestamp(Y), Y != si_1, Y != fn_1. leq(0,si_1, fn_1). leq(0,fn_1, si_1)."

# FT_23: fn_1 < si_1 = si_2 = si_3 = si_4 = fn_2 = fn_3 = fn_4
FT_23 = "leq(0,X,X) :-   timestamp(X). leq(0,X,Y) :-   timestamp(X), timestamp(Y), Y != fn_1."
# FT_24: fn_1 < si_1 < si_2 = si_3 = si_4 = fn_2 = fn_3 = fn_4
FT_24 = "leq(0,X,X) :-   timestamp(X). leq(0,X,Y) :-   timestamp(X), timestamp(Y), Y != si_1, Y != fn_1. leq(0, fn_1, si_1)."

# ==============================================================================
# List of initial NTFS timestamp strucutures due tofile tunneling
# ==============================================================================

ntfs_initial_TS_FT = list({FT_11, FT_12, FT_13, FT_14, 
                           FT_21, FT_22, FT_23, FT_24})


# ==============================================================================
# List of initial NTFS timestamp strucutures including file tunneling
# ==============================================================================

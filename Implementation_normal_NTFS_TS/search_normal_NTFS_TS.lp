% ---------------------------------------------------
% 1.1.  NTFS timestamps variables
% ---------------------------------------------------

% Define timestamp variables T for NTFS
timestamp(si_1). timestamp(si_2). timestamp(si_3). timestamp(si_4). 
timestamp(fn_1). timestamp(fn_2). timestamp(fn_3). timestamp(fn_4).

% si_i belongs to SI information
si(si_1). si(si_2). si(si_3). si(si_4).

% fn_i belongs to FN information
fn(fn_1). fn(fn_2). fn(fn_3). fn(fn_4).

% Define a mapping between si_i and fn_i
map(si_1,fn_1). map(si_2,fn_2). map(si_3,fn_3). map(si_4,fn_4).


% ---------------------------------------------------
% 1.2.  Starting Timestamp Structure
% ---------------------------------------------------
 
% Note: For each search, exaclty one starting NTFS timestamp structure is added by main.py.
%       Starting structures are defined by facts of the form "leq(0,X,Y).".
%       "leq(0,X,Y)." denotes that at state 0 (start), Y ia ranked at least as high as X.

% ---------------------------------------------------
% 1.3.  Compositions of NTFS file operations
% ---------------------------------------------------

% Note: For each search, exaclty one composition of NTFS operations is added by main.py. 
%       Compositions of NTFS operations are defined by facts of the form "apply(S,operation_name)."
%       "apply(S,operation_name)." denotes that operation_name is perfomed at state S. 


finaloperation(N) :-
    apply(N,_),
    not apply(N+1,_).

% Since we have N operations subsequently applied, 
% we have N+1 many states with N+1 being the last state.

finalstate(N+1):- 
    finaloperation(N). 

state(0..N+1):-
    finaloperation(N).


% ===================================================
% 2.    DEFINITION NTFS FILE OPERATIONS
% ===================================================

% ---------------------------------------------------
% 2.1.  Access (AC)
% ---------------------------------------------------

% Structure restricted to T unchanged
leq(S+1,X,Y):- 
    apply(S,operation_ac),
    leq(S,X,Y).

% ---------------------------------------------------
% 2.2.  Attribute Change (AT)
% ---------------------------------------------------

%  Structure restricted to T/{si_3} unchanged
leq(S+1,X,Y):- 
    apply(S,operation_at),
    leq(S,X,Y), 
    X != si_3, Y != si_3.

% si_3 value becomes maximal timestamp variable in S+1
leq(S+1,X,si_3):- 
    apply(S,operation_at),
    timestamp(X).

% Allow ties for si_3:
{ leq(S+1,si_3,X) }:-
    apply(S,operation_at),
    timestamp(X).

% ---------------------------------------------------
% 2.3.  Update (UP)
% ---------------------------------------------------

%  Structure restricted to T/{si_2,si_3} unchanged
leq(S+1,X,Y):- 
    apply(S,operation_up),
    leq(S,X,Y), 
    X != si_2, Y != si_2, 
    X != si_3, Y != si_3. 

% si_3 value becomes second-to-maximal timestamp variable in S+1
leq(S+1,X,si_3):- 
    apply(S,operation_up),
    timestamp(X),
    X != si_2.

% si_2 value becomes maximal timestamp variable in S+1
leq(S+1,X,si_2):- 
    apply(S,operation_up),
    timestamp(X).

% Allow ties for si_3:
{ leq(S+1,si_3,X) }:-
    apply(S,operation_up),
    timestamp(X).

% Allow ties for si_2:
{ leq(S+1,si_2,X) }:-
    apply(S,operation_up),
    timestamp(X).

% ----------------------------------------------------
% 2.4. Overwriting Copy (OC)
% ----------------------------------------------------

%  Structure restricted to T/{si_2,si_3} unchanged
leq(S+1,X,Y):- 
    apply(S,operation_oc),
    leq(S,X,Y), 
    X != si_2, Y != si_2, 
    X != si_3, Y != si_3. 

% si_3 becomes maximal timestamp variable in S+1
leq(S+1,X,si_3) :- 
    apply(S,operation_oc),
    timestamp(X).

% Allow ties for si_3:
{ leq(S+1,si_3,X) }:-
    apply(S,operation_oc),
    timestamp(X).

% Generate Reflexivity for si_2:
leq(S+1,si_2,si_2) :- 
    apply(S,operation_oc).

% Choose the position of si_2
{ leq(S+1,si_2,Z) ; leq(S+1,Z,si_2) } 2 :- 
    apply(S,operation_oc),
    timestamp(Z), 
    Z != si_2, Z != si_3.


% ----------------------------------------------------
% 2.5. Overwriting From Another Volume (OV)
% ----------------------------------------------------

% Structure restricted to T/{si_1,si_2,si_3} unchanged
leq(S+1,X,Y):- 
    apply(S,operation_ov),
    leq(S,X,Y),
    X != si_1, Y != si_1,
    X != si_2, Y != si_2, 
    X != si_3, Y != si_3. 

% si_3 becomes maximal timestamp variable in S+1
leq(S+1,X,si_3) :-
    apply(S,operation_ov),
    timestamp(X).

% Allow ties for si_3:
{ leq(S+1,si_3,X) }:-
    apply(S,operation_ov),
    timestamp(X).

% Generate Reflexivity for si_1:
leq(S+1,si_1,si_1) :- 
    apply(S,operation_ov).

% Generate Reflexivity for si_2:
leq(S+1,si_2,si_2) :- 
    apply(S,operation_ov).

% Choose the position of si_1 in S+1
{ leq(S+1,si_1,Z) ; leq(S+1,Z,si_1) } 2 :- 
    apply(S,operation_ov),
    timestamp(Z), 
    Z != si_1, Z != si_2, Z != si_3.

% Choose the position of si_2 in S+1
{ leq(S+1,si_2,Z) ; leq(S+1, Z,si_2) } 2 :- 
    apply(S,operation_ov),
    timestamp(Z), 
    Z != si_1, Z != si_2, Z != si_3.

% Choose relative ranking of si_1 & si_2 in S+1

{ leq(S+1, si_1, si_2); leq(S+1,si_2, si_1) } 2 :-
    apply(S,operation_ov).

% ----------------------------------------------------
% 2.6. Rename (RE)
% ----------------------------------------------------

% Structure restricted to {si_1,si_2,si_4} unchanged
leq(S+1,X,Y):- 
    apply(S,operation_re),
    si(X), 
    si(Y), 
    X != si_3, Y != si_3, 
    leq(S,X,Y).

% fn_i =< fn_j in S+1 if and only if si_i =< si_j in S
leq(S+1,X,Y):- 
    apply(S,operation_re),
    fn(X), 
    fn(Y),
    map(X_SI,X), 
    map(Y_SI,Y),
    leq(S,X_SI,Y_SI).

% fn_i =< si_j in S+1 if and only if si_i =< si_j in S 
% Exception: si_j = si_3
leq(S+1,X,Y):- 
    apply(S,operation_re),
    fn(X),
    si(Y), 
    map(X_SI,X), 
    leq(S,X_SI,Y),
    Y != si_3.

% si_i =< fn_j in S+1 if and only if si_i =< si_j in S 
% Exception: si_i = si_3
leq(S+1,X,Y):- 
    apply(S,operation_re),
    si(X),
    fn(Y),
    map(Y_SI,Y),
    leq(S,X,Y_SI),
    X != si_3.

% si_3 becomes maximal timestamp variable in S+1
leq(S+1,X,si_3) :- 
    apply(S,operation_re),
    timestamp(X).

% Allow ties for si_3:
{ leq(S+1,si_3,X) }:-
    apply(S,operation_re),
    timestamp(X).

% ===================================================
% 3. UNIVERSAL CONSTRAINTS FOR TOTAL PREORDER
% ===================================================

% Reflexivity
:-  state(S),
    timestamp(X),
    not leq(S,X,X).

% Transitivity
:-  state(S),
    timestamp(X), timestamp(Y), timestamp(Z),
    leq(S,X,Y), leq(S,Y,Z), not leq(S,X,Z).

% Totality
:-  state(S),
    timestamp(X), timestamp(Y),
    X != Y,
   not leq(S,X,Y), not leq(S,Y,X).


% ===================================================
% 4.    OUTPUT TIMESTAMP STRUCTURES
% ===================================================

% ---------------------------------------------------
% 4.1 Generate Ouput Timestamp Structure
% ---------------------------------------------------

% Note: finaloperation(N) provides the last operation applied
%       yielding the final timestamp structure defined by leq(N+1,_,_) with state(M) = state(N+1)

leq_output(X,Y):-
    finalstate(M),
    leq(M,X,Y).

% ---------------------------------------------------
% 4.1. Simple Representation of Output Structure
% ---------------------------------------------------

same_rank(X,Y):- 
    leq_output(X,Y), leq_output(Y,X).

higher_rank(X,Y):- 
    leq_output(X,Y), not leq_output(Y,X).

rank(X,N):- 
    same_rank(X,X), 
    N = #count {Y : higher_rank (Y,X) }.
% Facts about males in the Modern Family
male(jay).
male(phil).
male(manny).
male(joe).
male(mitchell).
male(cameron).
male(luke).

% Facts about females in the Modern Family
female(claire).
female(gloria).
female(haley).
female(alex).
female(lily).

% Parent relationships
parent(phil, haley).
parent(phil, alex).
parent(phil, luke).
parent(claire, haley).
parent(claire, alex).
parent(claire, luke).

parent(jay, manny).
parent(jay, joe).
parent(gloria, manny).
parent(gloria, joe).

parent(mitchell, lily).
parent(cameron, lily).

parent(jay, mitchell).
parent(jay, claire).

% Pet relationships
pet(stella, jay).        % Stella is Jays pet dog
pet(larry, mitchell).    % Larry is Mitchell and Camerons pet cat

% Rules to determine mother and father
mother(X, Y) :- parent(X, Y), female(X).
father(X, Y) :- parent(X, Y), male(X).

% Rules to determine sons and daughters
son(X, Y) :- parent(Y, X), male(X).
daughter(X, Y) :- parent(Y, X), female(X).

% Rule to determine grandparents
grandparent(X, Y) :- parent(X, Z), parent(Z, Y).

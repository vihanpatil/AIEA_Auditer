
    % Facts about chlorophyll and its role in photosynthesis
    chlorophyll_present_in(grass).
    chlorophyll_present_in(chloroplasts).
    chlorophyll_role(photosynthesis).

    % Facts about light absorption and reflection by chlorophyll
    absorbs_light(chlorophyll, blue, 430, 450).
    absorbs_light(chlorophyll, red, 640, 680).
    reflects_light(chlorophyll, green, 500, 550).

    % Rule to determine why grass appears green
    appears_green(X) :-
        chlorophyll_present_in(X),
        reflects_light(chlorophyll, green, _, _).

    % Rule to determine the perception of green color
    perceive_color(X, green) :-
        appears_green(X).
    
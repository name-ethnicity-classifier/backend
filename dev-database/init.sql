CREATE TABLE model (
    nationalities TEXT[]                 NOT NULL,
    accuracy      DOUBLE PRECISION,
    scores        REAL[],
    is_trained    BOOLEAN DEFAULT false  NOT NULL,
    is_grouped    BOOLEAN DEFAULT false  NOT NULL,
    is_custom     BOOLEAN                NOT NULL,
    creation_time VARCHAR(64)            NOT NULL,
    id            VARCHAR(40)            NOT NULL CONSTRAINT model_pk PRIMARY KEY
);

CREATE TABLE "user" (
    email       VARCHAR(320)           NOT NULL,
    password    VARCHAR(64)            NOT NULL,
    name        VARCHAR(64)            NOT NULL,
    role        VARCHAR(32)            NOT NULL,
    signup_time VARCHAR(64)            NOT NULL,
    verified    BOOLEAN DEFAULT false  NOT NULL,
    consented   BOOLEAN DEFAULT false  NOT NULL,
    id          SERIAL                 NOT NULL CONSTRAINT user_pk PRIMARY KEY
);


CREATE TABLE user_to_model (
    user_id  INTEGER     NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    model_id VARCHAR(40) NOT NULL REFERENCES "model"(id) ON DELETE CASCADE,
    name     VARCHAR(40) NOT NULL,
    id       SERIAL      NOT NULL CONSTRAINT user_to_model_pk PRIMARY KEY
);


ALTER TABLE model OWNER TO postgres;

INSERT INTO public.model (accuracy, nationalities, scores, is_trained, is_grouped, is_custom, creation_time, id) 
VALUES (83.55, '{african,celtic,eastAsian,european,hispanic,muslim,nordic,southAsia}', 
        '{0.762470006942749,0.7657300233840942,0.9311699867248535,0.7971600294113159,0.885129988193512,0.8356500267982483,0.8405900001525879,0.8633999824523926}', 
        true, true, false, '2021-10-14 16:44:00', '8_nationality_groups');
INSERT INTO public.model (accuracy, nationalities, scores, is_trained, is_grouped, is_custom, creation_time, id) 
VALUES (78.51, '{else,british,indian,spanish,german,italian,french,chinese,japanese,dutch,russia}', 
        '{0.3926999866962433,0.6724200248718262,0.8446999788284302,0.8085700273513794,0.7493199706077576,0.8261500000953674,0.7379400134086609,0.9672300219535828,0.9860699772834778,0.7153800129890442,0.9139000177383423}', 
        true, false, false, '2021-09-07 12:11:00', '10_nationalities_and_else');
INSERT INTO public.model (accuracy, nationalities, scores, is_trained, is_grouped, is_custom, creation_time, id) 
VALUES (74.99, '{british,norwegian,indian,irish,spanish,american,german,polish,bulgarian,turkish,pakistani,italian,romanian,french,australian,chinese,swedish,nigerian,dutch,filipin}', 
        '{0.36866000294685364,0.7852200269699097,0.8133400082588196,0.6620399951934814,0.7920200228691101,0.4155200123786926,0.6982700228691101,0.9381499886512756,0.9475899934768677,0.9218000173568726,0.8444300293922424,0.8109800219535828,0.9209799766540527,0.715719997882843,0.2766000032424927,0.9574099779129028,0.6868299841880798,0.8658499717712402,0.6825900077819824,0.7980999946594238}', 
        true, false, false, '2021-09-07 16:36:00', '20_most_occuring_nationalities');
INSERT INTO public.model (accuracy, nationalities, scores, is_trained, is_grouped, is_custom, creation_time, id) 
VALUES (78.41, '{british,else,indian,spanish,american,german,polish,pakistani,italian,romanian,french,chinese,nigerian,japanese,russia}', 
        '{0.5186200141906738,0.3864000141620636,0.8155099749565125,0.7952600121498108,0.47832000255584717,0.7324699759483337,0.9356499910354614,0.8660799860954285,0.8185700178146362,0.9142000079154968,0.7210900187492371,0.9594299793243408,0.8811600208282471,0.976360023021698,0.8934000134468079}', 
        true, false, false, '2021-07-20 12:34:00', '14_nationalities_and_else');
INSERT INTO public.model (accuracy, nationalities, scores, is_trained, is_grouped, is_custom, creation_time, id) 
VALUES (98.55, '{else,chinese}', '{0.985450029373169,0.9855999946594238}', 
        true, false, false, '2021-07-20 13:41:00', 'chinese_and_else');

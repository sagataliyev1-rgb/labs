% =========================================================
% Лабораторная работа № 10: Логическое программирование в SWI-Prolog
% =========================================================

% --- Задание 1: Исходная база знаний (студенты, курсы, освоения, пререквизиты) ---
student(aida).
student(miras).
student(dana).
student(timur).
student(aliya). % добавленный студент (Задание 1)

course(programming_1).
course(programming_2).
course(data_structures).
course(databases).
course(artificial_intelligence).
course(machine_learning).

% completed(Student, Course)
completed(aida, programming_1).
completed(aida, programming_2).
completed(aida, data_structures).
completed(aida, databases).

completed(miras, programming_1).
completed(miras, databases).

completed(dana, programming_1).
completed(dana, programming_2).
completed(dana, data_structures).

completed(timur, programming_1).

% Два факта об освоенных дисциплинах для aliya (Задание 1)
completed(aliya, programming_1).
completed(aliya, programming_2).

% requires(Course, Prerequisite)
requires(programming_2, programming_1).
requires(data_structures, programming_2).
requires(artificial_intelligence, data_structures).
requires(artificial_intelligence, databases).
requires(machine_learning, artificial_intelligence).

% Примечание: циклический факт из Задания 7 закомментирован после эксперимента,
% чтобы не мешать обычному поиску:
% requires(programming_1, machine_learning).


% --- Задание 2: Правила и составные цели ---
ai_candidate(Student) :-
    completed(Student, data_structures),
    completed(Student, databases).

strong_student(Student) :-
    completed(Student, programming_2),
    completed(Student, data_structures).


% --- Задание 4: Проверка непосредственного допуска ---
missing_direct(Student, Course, Prerequisite) :-
    student(Student),
    requires(Course, Prerequisite),
    \+ completed(Student, Prerequisite).

immediate_eligible(Student, Course) :-
    student(Student),
    course(Course),
    \+ missing_direct(Student, Course, _).


% --- Задание 5: Транзитивные (рекурсивные) пререквизиты ---
prerequisite(Course, Prerequisite) :-
    requires(Course, Prerequisite).

prerequisite(Course, Prerequisite) :-
    requires(Course, Intermediate),
    prerequisite(Intermediate, Prerequisite).


% --- Задание 6: Полный допуск и список недостающих курсов ---
missing_all(Student, Course, Missing) :-
    setof(P,
          (prerequisite(Course, P), \+ completed(Student, P)),
          Missing), !.
missing_all(_, _, []).

eligible(Student, Course) :-
    student(Student),
    course(Course),
    missing_all(Student, Course, []).


% --- Задание 7: Безопасность рекурсии с контролем посещённых узлов ---
safe_prerequisite(Course, Prerequisite) :-
    safe_prerequisite(Course, Prerequisite, [Course]).

safe_prerequisite(Course, Prerequisite, _) :-
    requires(Course, Prerequisite).

safe_prerequisite(Course, Prerequisite, Visited) :-
    requires(Course, Next),
    \+ memberchk(Next, Visited),
    safe_prerequisite(Next, Prerequisite, [Next | Visited]).


% --- Задание 8: Интегрированный отчёт / рекомендация ---
recommendation(Student, Course, eligible, []) :-
    eligible(Student, Course).

recommendation(Student, Course, missing, Missing) :-
    missing_all(Student, Course, Missing),
    Missing \= [].


% =========================================================
% Индивидуальный вариант № 2: Запись на курс (can_enroll/2)
% =========================================================

% Дополнительные факты: лимит мест и текущее количество записанных студентов
course_capacity(programming_1, 30).
course_capacity(programming_2, 25).
course_capacity(data_structures, 20).
course_capacity(databases, 20).
course_capacity(artificial_intelligence, 15).
course_capacity(machine_learning, 10).

enrolled_count(programming_1, 30).
enrolled_count(programming_2, 20).
enrolled_count(data_structures, 18).
enrolled_count(databases, 19).
enrolled_count(artificial_intelligence, 14).
enrolled_count(machine_learning, 10).

% Вспомогательное правило: проверка наличия свободных мест на курсе
has_free_seat(Course) :-
    course(Course),
    course_capacity(Course, Capacity),
    enrolled_count(Course, Enrolled),
    Enrolled < Capacity.

% Основной предикат варианта 2: студент может записаться на курс,
% если выполнены все пререквизиты и есть свободные места.
can_enroll(Student, Course) :-
    eligible(Student, Course),
    has_free_seat(Course).

% Рекурсивная фильтрация списка пререквизитов с базовым и рекурсивным случаями
collect_missing([], _, []).
collect_missing([P | Rest], Student, [P | MissingRest]) :-
    \+ completed(Student, P),
    collect_missing(Rest, Student, MissingRest).
collect_missing([P | Rest], Student, MissingRest) :-
    completed(Student, P),
    collect_missing(Rest, Student, MissingRest).

CREATE TABLE categories (
    id serial PRIMARY KEY,
    name text NOT NULL,
    parent_id int NULL,
    UNIQUE(name, parent_id)
);

-- CREATE TABLES trips, participants

CREATE TABLE expenses (
    id serial PRIMARY KEY,
    category_id int REFERENCES categories (id) NULL,
    amount float NOT NULL,
    -- should be payer_id in future
    payer text NOT NULL,
    -- structure {"<payer_name>": "<proportion>", ...}
    -- should contain participant_id instead of payer_name in future
    proportions jsonb NOT NULL
    -- description
    -- created_at
);


-- Таблица: [кому] – [кто] – [сколько должен]
WITH detbs AS (
    -- Сумма долгов по каждой стороне отношений
    -- Например, A должен B 10, B должен A 30
    SELECT
           t.payer,
           t.debtor,
           SUM(t.amount) AS amount
    FROM (
            -- Распаковка JSON в таблицу и отсеивание плательщика из пропорций
            SELECT
                   exp.payer,
                   prop.key AS debtor,
                   prop.value::float AS amount
            FROM
                 expenses exp,
                 jsonb_each(exp.proportions) prop
            WHERE exp.payer != prop.key
        ) t
    GROUP BY t.payer, t.debtor
)
-- Результирующая сумма долгов по наибольшему долгу
-- Например, если A должен B 10, B должен A 30, то результат будет B должен A 20
SELECT *
FROM (
     SELECT
        d1.payer,
        d1.debtor,
        -- При LEFT JOIN может на найтись пары, поэтому в этом случае разница будет равна NULL
        -- и нужно взять существующее значение долга
        COALESCE(d1.amount - d2.amount, d1.amount) AS amount
     FROM detbs d1 LEFT JOIN detbs d2 ON d1.payer = d2.debtor AND d1.debtor = d2.payer
) t
WHERE t.amount > 0;


-- Таблица: [кто] – [сколько потратил]
SELECT
       prop.key AS person,
       SUM(prop.value::float) AS amount
FROM
     expenses exp,
     jsonb_each(exp.proportions) prop
GROUP BY prop.key;


-- Таблица: [категория] – [кто сколько потратил] ({"<person>": "<expense>", ...})
-- Сумма трат для категории и надкатегории и для каждой персоны
WITH RECURSIVE r AS (
    SELECT
           category_id,
           person,
           amount
    FROM exp

    UNION

    SELECT
           COALESCE(c.parent_id, c.id),
           r.person,
           r.amount + COALESCE(p_exp.amount, 0)
    FROM r
        INNER JOIN categories c ON r.category_id = c.id
        LEFT JOIN exp p_exp ON c.parent_id = p_exp.category_id AND p_exp.person = r.person
),
-- Сумма трат для каждой категории и для каждой персоны
exp AS (
    SELECT
       t.category_id,
       t.person,
       SUM(t.amount) AS amount
    FROM (
            SELECT
                   exp.category_id,
                   prop.key AS person,
                   prop.value::float AS amount
            FROM
                 expenses exp,
                 jsonb_each(exp.proportions) prop
        ) t
GROUP BY t.category_id, t.person
),
sum_exp AS (
    -- Отсеивание предыдущих итераций по категориям и персонам
    -- (берется маскимум из amount, так как рекурсия работает итерацинно)
    SELECT category_id, person, MAX(amount) AS amount
    FROM r
    GROUP BY category_id, person
)
SELECT category_id, jsonb_object_agg(person, amount) AS amount
FROM sum_exp
GROUP BY category_id;


-- Обход категорий
WITH RECURSIVE r AS (
    SELECT id, parent_id, name, 1 AS level
    FROM categories
-- Можно выбрать, от какой категории нужны подкатегори
--     WHERE id = 1
    WHERE parent_id IS NULL

    UNION

    SELECT c.id, c.parent_id, c.name, r.level + 1 AS level
    FROM r INNER JOIN categories c ON c.parent_id = r.id
)
SELECT * FROM r;
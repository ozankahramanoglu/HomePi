DROP TABLE IF EXISTS public.bot_user CASCADE ;
DROP TABLE IF EXISTS public.status ;

CREATE TABLE IF NOT EXISTS public.status(
    id INT primary key ,
    status varchar(140)
                          );

CREATE TABLE IF NOT EXISTS public.bot_user(
    id INT primary key ,
    firstName varchar(140) NOT NULL,
    lastName varchar(140),
    userName varchar(140),
    isbot bool,
    languageCode varchar(10),
    locationShare int DEFAULT 1,
    ContractShare int DEFAULT 1,
    status INT,
    FOREIGN KEY (status)
        REFERENCES public.status(id)
        ON DELETE CASCADE              );



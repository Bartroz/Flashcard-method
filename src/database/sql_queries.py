
tableExistQuery: str = """ SELECT name 
                        FROM sqlite_master
                        WHERE type = 'table'
                        AND name = ? """

createTableQuery: str = """ CREATE Table IF NOT EXISTS Words (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            word TEXT NOT NULL UNIQUE,
                            meaning1 TEXT NOT NULL,
                            meaning2 TEXT,
                            meaning3 TEXT,
                            box INTEGER DEFAULT 0,
                            total_attempts INTEGER DEFAULT 0,
                            total_correct INTEGER DEFAULT 0,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            last_reviewed_at TIMESTAMP
                        ); """

countQuery: str = """ SELECT COUNT(*) FROM Words """

addWordQuery: str = """ INSERT OR IGNORE INTO Words
                    (word, meaning1, meaning2, meaning3)
                    VALUES (?,?,?,?) """

downloadNewWordsQuery: str = """ SELECT word, meaning1, meaning2, meaning3
                            FROM Words
                            WHERE box = 0; """

downloadWordsForContinuationQuery: str = """ SELECT word, meaning1, meaning2, meaning3
                                        FROM Words
                                        WHERE box >= 1
                                            AND box < 5
                                            AND (
                                            total_attempts < 3
                                            OR
                                            (total_correct * 1.0 / total_attempts) >= 0.6
                                            ) """ 

downloadDifficultWordsQuery: str = """ SELECT word, meaning1, meaning2, meaning3
                                    FROM Words
                                    WHERE total_attempts >= 3
                                    AND (total_correct * 1.0 / total_attempts) < 0.6 """

correctWordsQuery: str = """ UPDATE Words  
                        SET box = CASE 
                                WHEN box < 5 THEN box + 1
                                ELSE 5
                            END,
                        total_attempts = total_attempts + 1,
                        total_correct = total_correct + 1,
                        last_reviewed_at = CURRENT_TIMESTAMP
                        WHERE word = ? """

incorrectWordsQuery: str = """ UPDATE Words  
                        SET total_attempts = total_attempts + 1,
                        total_correct = 0,
                        last_reviewed_at = CURRENT_TIMESTAMP
                        WHERE word = ? """


-- SQLite Database Schema for QuizApp
-- Converted from MySQL schema

-- Table: longqa
CREATE TABLE IF NOT EXISTS `longqa` (
  `longqa_qid` INTEGER PRIMARY KEY AUTOINCREMENT,
  `test_id` TEXT NOT NULL,
  `qid` TEXT NOT NULL,
  `q` TEXT NOT NULL,
  `marks` INTEGER DEFAULT NULL,
  `uid` INTEGER DEFAULT NULL
);

-- Table: longtest
CREATE TABLE IF NOT EXISTS `longtest` (
  `longtest_qid` INTEGER PRIMARY KEY AUTOINCREMENT,
  `email` TEXT NOT NULL,
  `test_id` TEXT NOT NULL,
  `qid` INTEGER NOT NULL,
  `ans` TEXT NOT NULL,
  `marks` INTEGER NOT NULL,
  `uid` INTEGER NOT NULL
);

-- Table: practicalqa
CREATE TABLE IF NOT EXISTS `practicalqa` (
  `pracqa_qid` INTEGER PRIMARY KEY AUTOINCREMENT,
  `test_id` TEXT NOT NULL,
  `qid` TEXT NOT NULL,
  `q` TEXT NOT NULL,
  `compiler` INTEGER NOT NULL,
  `marks` INTEGER NOT NULL,
  `uid` INTEGER NOT NULL
);

-- Table: practicaltest
CREATE TABLE IF NOT EXISTS `practicaltest` (
  `pid` INTEGER PRIMARY KEY AUTOINCREMENT,
  `email` TEXT NOT NULL,
  `test_id` TEXT NOT NULL,
  `qid` TEXT NOT NULL,
  `code` TEXT,
  `input` TEXT,
  `executed` TEXT DEFAULT NULL,
  `marks` INTEGER NOT NULL,
  `uid` INTEGER NOT NULL
);

-- Table: proctoring_log
CREATE TABLE IF NOT EXISTS `proctoring_log` (
  `pid` INTEGER PRIMARY KEY AUTOINCREMENT,
  `email` TEXT NOT NULL,
  `name` TEXT NOT NULL,
  `test_id` TEXT NOT NULL,
  `voice_db` INTEGER DEFAULT 0,
  `img_log` TEXT NOT NULL,
  `user_movements_updown` INTEGER NOT NULL,
  `user_movements_lr` INTEGER NOT NULL,
  `user_movements_eyes` INTEGER NOT NULL,
  `phone_detection` INTEGER NOT NULL,
  `person_status` INTEGER NOT NULL,
  `log_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `uid` INTEGER NOT NULL
);

-- Table: questions
CREATE TABLE IF NOT EXISTS `questions` (
  `questions_uid` INTEGER PRIMARY KEY AUTOINCREMENT,
  `test_id` TEXT NOT NULL,
  `qid` TEXT NOT NULL,
  `q` TEXT NOT NULL,
  `a` TEXT NOT NULL,
  `b` TEXT NOT NULL,
  `c` TEXT NOT NULL,
  `d` TEXT NOT NULL,
  `ans` TEXT NOT NULL,
  `marks` INTEGER NOT NULL,
  `uid` INTEGER NOT NULL
);

-- Table: students
CREATE TABLE IF NOT EXISTS `students` (
  `sid` INTEGER PRIMARY KEY AUTOINCREMENT,
  `email` TEXT NOT NULL,
  `test_id` TEXT NOT NULL,
  `qid` TEXT DEFAULT NULL,
  `ans` TEXT,
  `uid` INTEGER NOT NULL
);

-- Table: studenttestinfo
CREATE TABLE IF NOT EXISTS `studenttestinfo` (
  `stiid` INTEGER PRIMARY KEY AUTOINCREMENT,
  `email` TEXT NOT NULL,
  `test_id` TEXT NOT NULL,
  `time_left` INTEGER NOT NULL,  -- Changed from TIME to INTEGER (seconds)
  `completed` INTEGER DEFAULT 0,
  `uid` INTEGER NOT NULL
);

-- Table: teachers
CREATE TABLE IF NOT EXISTS `teachers` (
  `tid` INTEGER PRIMARY KEY AUTOINCREMENT,
  `email` TEXT NOT NULL,
  `test_id` TEXT NOT NULL,
  `test_type` TEXT NOT NULL,
  `start` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `end` TIMESTAMP NOT NULL,
  `duration` INTEGER NOT NULL,
  `show_ans` INTEGER NOT NULL,
  `password` TEXT NOT NULL,
  `subject` TEXT NOT NULL,
  `topic` TEXT NOT NULL,
  `neg_marks` INTEGER NOT NULL,
  `calc` INTEGER NOT NULL,
  `proctoring_type` INTEGER NOT NULL DEFAULT 0,
  `uid` INTEGER NOT NULL
);

-- Table: users
CREATE TABLE IF NOT EXISTS `users` (
  `uid` INTEGER PRIMARY KEY AUTOINCREMENT,
  `name` TEXT NOT NULL,
  `email` TEXT UNIQUE NOT NULL,
  `password` TEXT NOT NULL,
  `register_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `user_type` TEXT NOT NULL,
  `user_image` TEXT NOT NULL,
  `user_login` INTEGER NOT NULL,
  `examcredits` INTEGER NOT NULL DEFAULT 7
);

-- Table: window_estimation_log
CREATE TABLE IF NOT EXISTS `window_estimation_log` (
  `wid` INTEGER PRIMARY KEY AUTOINCREMENT,
  `email` TEXT NOT NULL,
  `test_id` TEXT NOT NULL,
  `name` TEXT NOT NULL,
  `window_event` INTEGER NOT NULL,
  `transaction_log` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `uid` INTEGER NOT NULL
);

-- Create indexes
CREATE INDEX IF NOT EXISTS `idx_longqa_uid` ON `longqa` (`uid`);
CREATE INDEX IF NOT EXISTS `idx_longtest_uid` ON `longtest` (`uid`);
CREATE INDEX IF NOT EXISTS `idx_practicalqa_uid` ON `practicalqa` (`uid`);
CREATE INDEX IF NOT EXISTS `idx_practicaltest_uid` ON `practicaltest` (`uid`);
CREATE INDEX IF NOT EXISTS `idx_proctoring_log_email` ON `proctoring_log` (`email`);
CREATE INDEX IF NOT EXISTS `idx_proctoring_log_email_test` ON `proctoring_log` (`email`, `test_id`);
CREATE INDEX IF NOT EXISTS `idx_proctoring_log_uid` ON `proctoring_log` (`uid`);
CREATE INDEX IF NOT EXISTS `idx_questions_uid` ON `questions` (`uid`);
CREATE INDEX IF NOT EXISTS `idx_students_uid` ON `students` (`uid`);
CREATE INDEX IF NOT EXISTS `idx_studenttestinfo_uid` ON `studenttestinfo` (`uid`);
CREATE INDEX IF NOT EXISTS `idx_teachers_uid` ON `teachers` (`uid`);
CREATE INDEX IF NOT EXISTS `idx_window_estimation_log_uid` ON `window_estimation_log` (`uid`);

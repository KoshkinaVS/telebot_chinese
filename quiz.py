import terms_work
import words_work

from random import choices


class Quiz:
    def __init__(self):
        random_terms = choices(words_work.get_terms_for_table(), k=5)  #TODO: вынести количество вопросов в .env

        self.qna = []
        cnt = 0
        for rt in random_terms:
            qna_item = []
            cnt += 1
            qna_item.append(cnt)
            qna_item = qna_item + rt[1:]
            self.qna.append(qna_item)

            self.user_answers = []
            self.qna_iter = iter(self.qna)  # Объект-итератор для вопросов-ответов

    def next_qna(self):
        """Возвращает очередной вопрос"""
        return next(self.qna_iter)

    def record_user_answer(self, a):
        """Добавляет ответ пользователя в переменную экземпляра (список ответов)"""
        self.user_answers.append(a)

    def get_user_answers(self):
        """Возвращает список ответов пользователя"""
        return self.user_answers

    def check_quiz(self):
        """Проверяет ответы и возвращает список эмодзи"""
        correct_answers = [qna_item[3] for qna_item in self.qna]
        answers_true_false = [i == j for i, j in zip(self.user_answers, correct_answers)]
        answers_emoji = [str(atf).replace('False', '❌').replace('True', '✅') for atf in answers_true_false]
        return answers_emoji
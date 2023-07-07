
import os.path

if __name__ == '__main__':

    path = 'data'
    questions_file = os.path.join(path, 'questions.txt')
    questions = []
    qa_files = [f for f in os.listdir(path) if f.startswith('QA-')]
    if len(qa_files) > 0:
        with open(questions_file, 'w', encoding='utf-8') as q:
            for file in qa_files:
                with open(os.path.join(path, file), 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.startswith('问题：'):
                            question = line[3:]
                            if question not in questions:
                                questions.append(question)
                                q.write(question)
                                q.flush()

    pass

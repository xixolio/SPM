import os
from collections import defaultdict
import pandas as pd
import numpy as np

BASE_PATH = os.path.abspath(os.path.dirname(__file__))


class SPMProcessing:
    def __init__(self):
        form = 'test3.csv'
        scores = 'puntajes_2.csv'

        self.questions_df = pd.read_csv(BASE_PATH + '/forms/' + form)
        self.scores_df = pd.read_csv(BASE_PATH + '/scores/' + scores, delimiter=';')

        self.default_scores_dict = {'nunca': 1,
                                    'ocasionalmente': 2,
                                    'frecuentemente': 3,
                                    'siempre': 4,
                                    'no observado': -1}

        self.inversed_scores_dict = {'nunca': 4,
                                     'ocasionalmente': 3,
                                     'frecuentemente': 2,
                                     'siempre': 1,
                                     'no observado': -1}

        self.answers_with_inversed_scores = [1, 2, 3, 4, 5, 6, 7, 8]

        non_observed_scores_dict = {2: [1, 2, 3, 4, 5, 7, 8, 16, 18, 19, 28],
                                    }
        default_non_observed_scores = 1
        self.non_observed_scores_questions_dict = defaultdict(lambda: default_non_observed_scores)

        for key, columns in non_observed_scores_dict.items():
            for value in columns:
                self.non_observed_scores_questions_dict[value] = key

    def get_empty_results_df(self):
        results_columns = [col for col in self.questions_df.columns if col.split('.')[0].isdigit()]
        results_df = self.questions_df[results_columns]

        sections = set([int(col[0]) for col in results_columns])

        section_scores = {section: 0 for section in sections}

        section_numbers = [int(col.split('.')[0]) for col in results_columns]
        question_numbers = [int(col.split('[')[1].split('.')[0]) for col in results_columns]

        index = [np.array(section_numbers),
                 np.array(question_numbers)
                 ]

        results_dict = {'Seccion': section_numbers,
                        'Pregunta': question_numbers,
                        'Resultados': results_df.iloc[0].str.lower().values
                        }

        results_df = pd.DataFrame(results_dict)
        results_df['Puntaje'] = 0
        return results_df

    def get_results_with_scores(self, results_df):
        inversed_scores_index = results_df['Pregunta'].isin(self.answers_with_inversed_scores)
        default_scores_index = ~inversed_scores_index

        results_df.loc[default_scores_index, 'Puntaje'] = results_df[default_scores_index]['Resultados'].transform(
            lambda x: self.default_scores_dict[x])
        results_df.loc[inversed_scores_index, 'Puntaje'] = results_df[inversed_scores_index]['Resultados'].transform(
            lambda x: self.inversed_scores_dict[x])

        non_observed_index = results_df['Resultados'] == 'no observado'

        results_df.loc[non_observed_index, 'Puntaje'] = results_df[non_observed_index]['Pregunta'].transform(
            lambda x: self.non_observed_scores_questions_dict[x])

        return results_df



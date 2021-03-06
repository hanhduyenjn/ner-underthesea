from os.path import dirname, join
from languageflow.flow import Flow
from languageflow.model import Model
from languageflow.model.crf import CRF
from languageflow.transformer.tagged import TaggedTransformer
# from languageflow.validation.validation import TrainTestSplitValidation

from corpus.vlsp2016.load_data import load_data

if __name__ == '__main__':
    # =========================================================================#
    # Start an experiment with flow
    # =========================================================================#
    flow = Flow()
    flow.log_folder = join(dirname(__file__), "logs")

    # =========================================================================#
    #                               Data
    # =========================================================================#


    # for quick experiment
    # file = join(dirname(__file__), "corpus", "sample_vlsp_2016", "test.txt")
    # sentences = vlsp2016.load_data(file)

    # for evaluation
    # file = join(dirname(__file__), "corpus", "vlsp2016", "train.txt")
    # file = join(dirname(__file__), "corpus", "sample_vlsp_2016", "train.txt")
    # sentences = vlsp2016.load_data(file)

    # for saving model
    sentences = []
    for f in ["product.txt","color_org_location.txt","location.txt","train.txt"]: 
        #each file contains 3 columns except train-udts (4 columns) 
        file = join(dirname(__file__), "corpus", "vlsp2016", f)
        sentences += load_data(file) 
    # print(sentences)
    flow.data(sentences=sentences)

    # =========================================================================#
    #                                Transformer
    # =========================================================================#
    template = [
            "T[-2].lower", "T[-1].lower", "T[0].lower", "T[1].lower", "T[2].lower",
 
            "T[-1].isdigit", "T[0].isdigit", "T[1].isdigit",
 
            "T[-1].istitle", "T[0].istitle", "T[1].istitle",
            "T[0,1].istitle", "T[0,2].istitle",
 
            "T[-2].is_in_dict", "T[-1].is_in_dict", "T[0].is_in_dict", "T[1].is_in_dict", "T[2].is_in_dict",
            "T[-2,-1].is_in_dict", "T[-1,0].is_in_dict", "T[0,1].is_in_dict", "T[1,2].is_in_dict",
            "T[-2,0].is_in_dict", "T[-1,1].is_in_dict", "T[0,2].is_in_dict",
 
            # word unigram and bigram and trigram
            "T[-2]", "T[-1]", "T[0]", "T[1]", "T[2]",
            "T[-2,-1]", "T[-1,0]", "T[0,1]", "T[1,2]",
            "T[-2,0]", "T[-1,1]", "T[0,2]",
		
            # pos unigram and bigram
            "T[-3][1]", "T[-2][1]", "T[-1][1]","T[0][1]","T[1][1]",
            "T[-3,-2][1]", "T[-2,-1][1]","T[-1,0][1]","T[0,1][1]"
        ]

    transformer = TaggedTransformer(template)

    flow.transform(transformer)

    # =========================================================================#
    #                               Models
    # =========================================================================#
    crf_params = {
        'c1': 1.0,  # coefficient for L1 penalty
        'c2': 1e-3,  # coefficient for L2 penalty
        'max_iterations': 150,  
        # include transitions that are possible, but not observed
        'feature.possible_transitions': True
    }
    flow.add_model(Model(CRF(params=crf_params), "CRF"))

    # =========================================================================#
    #                              Evaluation
    # =========================================================================#
    flow.add_score('f1_chunk')
    flow.add_score('accuracy_chunk')

    # flow.set_validation(TrainTestSplitValidation(test_size=0.1))
    # flow.set_validation(TrainTestSplitValidation(test_size=0.3))

    flow.train()

    # flow.save_model("CRF", filename="ner_crf_20171006_template_2.model")

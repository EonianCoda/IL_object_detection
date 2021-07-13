# built-in
import argparse
# torch
import torch
from evaluator import Evaluator
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed


ROOT_DIR = "/home/deeplab307/Documents/Anaconda/Shiang/IL/"
DEFAULT_THRESHOLD = 0.05
DEFAULT_DEPTH = 50

def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

def get_val_parser(args=None):
    parser = argparse.ArgumentParser()
    # must set params
    
    parser.add_argument('--dataset', help='Dataset name, must contain name and years, for instance: voc2007,voc2012', default='voc2007')
    parser.add_argument('--epoch', help='the index of validation epochs', nargs='+', type=int)
    parser.add_argument('--state', type=int)
    parser.add_argument('--scenario', help='the scenario of states, must be "20", "19 1", "10 10", "15 1", "15 1 1 1 1"', type=int, nargs="+", default=[20])
    parser.add_argument('--threshold', help='the threshold for prediction default=0.05', type=float, default=DEFAULT_THRESHOLD)
    parser.add_argument('--just_val', help='whether predict or not',type=str2bool, default=False)
    parser.add_argument('--output_csv', help='whether output the csv file, default = True', type=str2bool, default=True)

    # always fixed
    parser.add_argument('--depth', help='Resnet depth, must be one of 18, 34, 50, 101, 152', type=int, default=DEFAULT_DEPTH)
    parser.add_argument('--root_dir', help='the root dir for training', default=ROOT_DIR)
    parser = vars(parser.parse_args(args))
    # set for origin Parmas, otherwise it will have error
    parser['warm_stage'] = 0
    parser['shuffle_class'] = False
    return parser




def main(args=None):
    parser = get_val_parser(args)
    evaluator = Evaluator(parser)

    def evaluation(epoch, pbar=None):
        evaluator.do_predict(epoch, pbar)
        evaluator.do_evaluation(epoch)

    epochs = list(set(parser['epoch']))

    print("Evaluate at state{} Epoch({})".format(parser['state'], parser['epoch']))
    
    
    if parser['just_val']:
        evaluator.validation_check(epochs)
        for epoch in epochs:
            evaluator.do_evaluation(epoch)
    else:
        evaluator.evaluation_check(epochs)
        with tqdm(total=len(evaluator.dataset) * len(epochs),position=0, leave=True) as pbar:
            with ThreadPoolExecutor(max_workers=len(epochs)) as ex:
                for epoch in epochs:
                    ex.submit(evaluation, epoch, pbar)
    if parser['output_csv']:
        evaluator.output_csv_file()

if __name__ == '__main__':
    assert torch.__version__.split('.')[0] == '1'
    if not torch.cuda.is_available():
        print("CUDA isn't abailable")
        exit(-1)
    main()

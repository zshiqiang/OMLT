import pytest
import keras

import pyomo.environ as pyo
from pyoml.opt.neuralnet import NeuralNetworkBlock, \
    FullSpaceContinuousFormulation, ReducedSpaceContinuousFormulation
from pyoml.opt.scaling import OffsetScaling
from pyoml.opt.keras_reader import load_keras_sequential
from pyoml.opt.tests.train_keras_models import get_data

def _test_keras_linear_131(keras_fname, reduced_space=False):
    x,y,x_test = get_data('131')

    nn = keras.models.load_model(keras_fname)
    net = load_keras_sequential(nn)

    assert net.n_inputs == 1
    assert net.n_outputs == 1
    assert net.n_hidden == 3
    assert len(net.weights) == 4
    assert len(net.biases) == 4
    assert len(net.activations) == 4

    m = pyo.ConcreteModel()
    m.neural_net_block = NeuralNetworkBlock()
    if reduced_space:
        formulation = ReducedSpaceContinuousFormulation(net)
    else:
        formulation = FullSpaceContinuousFormulation(net)
    m.neural_net_block.build_formulation(formulation)

    nn_outputs = nn.predict(x=x_test)
    for d in range(len(x_test)):
        m.neural_net_block.inputs[0].fix(x_test[d])
        status = pyo.SolverFactory('ipopt').solve(m, tee=False)
        pyo.assert_optimal_termination(status)
        assert abs(pyo.value(m.neural_net_block.outputs[0]) - nn_outputs[d][0]) < 1e-5

def _test_keras_linear_big(keras_fname, reduced_space=False):
    x,y,x_test = get_data('131')
    
    nn = keras.models.load_model(keras_fname)
    net = load_keras_sequential(nn)

    m = pyo.ConcreteModel()
    m.neural_net_block = NeuralNetworkBlock()
    if reduced_space:
        formulation = ReducedSpaceContinuousFormulation(net)
    else:
        formulation = FullSpaceContinuousFormulation(net)
    m.neural_net_block.build_formulation(formulation)

    nn_outputs = nn.predict(x=x_test)
    for d in range(len(x_test)):
        m.neural_net_block.inputs[0].fix(x_test[d])
        status = pyo.SolverFactory('ipopt').solve(m, tee=False)
        pyo.assert_optimal_termination(status)
        assert abs(pyo.value(m.neural_net_block.outputs[0]) - nn_outputs[d][0]) < 1e-5

def test_keras_linear_131_full():
    _test_keras_linear_131('./models/keras_linear_131')
    _test_keras_linear_131('./models/keras_linear_131_sigmoid')
    _test_keras_linear_131('./models/keras_linear_131_sigmoid_output_activation')
    _test_keras_linear_131('./models/keras_linear_131_sigmoid_softplus_output_activation')

def test_keras_linear_131_reduced():
    _test_keras_linear_131('./models/keras_linear_131', reduced_space=True)
    _test_keras_linear_131('./models/keras_linear_131_sigmoid', reduced_space=True)
    _test_keras_linear_131('./models/keras_linear_131_sigmoid_output_activation', reduced_space=True)
    _test_keras_linear_131('./models/keras_linear_131_sigmoid_softplus_output_activation', reduced_space=True)

def test_keras_linear_big():
    _test_keras_linear_big('./models/big', reduced_space=False)
    # too slow
    #_test_keras_linear_big('./models/big', reduced_space=True)

if __name__ == '__main__':
    test_keras_linear_131()
    test_keras_linear_big()
    

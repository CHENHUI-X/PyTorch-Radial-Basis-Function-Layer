import torch
import torch.nn as nn

# RBF Layer

class RBF(nn.Module):
    """
    Transforms incoming data using a given radial basis function:
    u_{i} = rbf(||x - c_{i}|| / s_{i})

    Arguments:
        in_features: size of each input sample
        out_features: size of each output sample

    Shape:
        - Input: (N, in_features) where N is an arbitrary batch size
        - Output: (N, out_features) where N is an arbitrary batch size

    Attributes:
        centers: the learnable centres of shape (out_features, in_features).
            The values are initialised from a standard normal distribution.
            Normalising inputs to have mean 0 and standard deviation 1 is
            recommended.
        
        log_sigmas: logarithm of the learnable scaling factors of shape (out_features).
        
        basis_func: the radial basis function used to transform the scaled
            distances.
    """

    def __init__(self, in_features, out_features, basis_func):
        super(RBF, self).__init__()
        self.in_features = in_features
        self.out_features = out_features

        # the centers and sigma is learnable
        self.centers = nn.Parameter(torch.Tensor(out_features, in_features))
        self.log_sigmas = nn.Parameter(torch.Tensor(out_features))

        self.basis_func = basis_func
        self.reset_parameters()

    def reset_parameters(self):
        nn.init.normal_(self.centers, 0, 1)
        nn.init.constant_(self.log_sigmas, 0)

    def forward(self, input):

        '''
        :param input:
            [ [ 0, 0, 0, 0, 0] ,
              [ 10,10,10,10,10,] ,
              [ 20,20,20,20,20,] ,
              [ 30,30,30,30,30,] ,
            ]  that's shape is ( 4,5 )
            means input_features num is 5
            assume output_features num is 2
        '''

        size = (input.size(0), self.out_features, self.in_features)
        # now size  is  ( 4 , 2 , 5)

        x = input.unsqueeze(1).expand(size)
        '''
        tensor([
                [[ 0.,  0.,  0.,  0.,  0.],
                 [ 0.,  0.,  0.,  0.,  0.]],
                [[10., 10., 10., 10., 10.],
                 [10., 10., 10., 10., 10.]],
                [[20., 20., 20., 20., 20.],
                 [20., 20., 20., 20., 20.]],
                [[30., 30., 30., 30., 30.],
                 [30., 30., 30., 30., 30.]]
             ])
        
        '''
        c = self.centers.unsqueeze(0).expand(size)
        '''
        assume centers is 
                [[  a , a ,  a , a , a],
                 [  b , b ,  b , b , b] ]
        
        then c is    
        tensor([[[  a , a ,  a , a , a],
                 [  b , b ,  b , b , b] ],
                [[  a , a ,  a , a , a],
                 [  b , b ,  b , b , b] ],
                [[  a , a ,  a , a , a],
                 [  b , b ,  b , b , b] ],
                [[  a , a ,  a , a , a],
                 [  b , b ,  b , b , b] ]])
        
        '''
        #  每个样本 都需要对 分别 减去 每一个center ,
        #  然后计算距离,然后求和得到在每个center上的weight

        distances = (x - c).pow(2).sum(-1).pow(0.5) / torch.exp(self.log_sigmas).unsqueeze(0)
        # the shape is torch.Size([4, 2])
        # 表示 4个样本 , 2个中心 相应的weight(or distances)

        return self.basis_func(distances)



# RBFs

def gaussian(alpha):
    phi = torch.exp(-1*alpha.pow(2))
    return phi

def linear(alpha):
    phi = alpha
    return phi

def quadratic(alpha):
    phi = alpha.pow(2)
    return phi

def inverse_quadratic(alpha):
    phi = torch.ones_like(alpha) / (torch.ones_like(alpha) + alpha.pow(2))
    return phi

def multiquadric(alpha):
    phi = (torch.ones_like(alpha) + alpha.pow(2)).pow(0.5)
    return phi

def inverse_multiquadric(alpha):
    phi = torch.ones_like(alpha) / (torch.ones_like(alpha) + alpha.pow(2)).pow(0.5)
    return phi

def spline(alpha):
    phi = (alpha.pow(2) * torch.log(alpha + torch.ones_like(alpha)))
    return phi

def poisson_one(alpha):
    phi = (alpha - torch.ones_like(alpha)) * torch.exp(-alpha)
    return phi

def poisson_two(alpha):
    phi = ((alpha - 2*torch.ones_like(alpha)) / 2*torch.ones_like(alpha)) \
    * alpha * torch.exp(-alpha)
    return phi

def matern32(alpha):
    phi = (torch.ones_like(alpha) + 3**0.5*alpha)*torch.exp(-3**0.5*alpha)
    return phi

def matern52(alpha):
    phi = (torch.ones_like(alpha) + 5**0.5*alpha + (5/3) \
    * alpha.pow(2))*torch.exp(-5**0.5*alpha)
    return phi

def basis_func_dict():
    """
    A helper function that returns a dictionary containing each RBF
    """
    
    bases = {'gaussian': gaussian,
             'linear': linear,
             'quadratic': quadratic,
             'inverse quadratic': inverse_quadratic,
             'multiquadric': multiquadric,
             'inverse multiquadric': inverse_multiquadric,
             'spline': spline,
             'poisson one': poisson_one,
             'poisson two': poisson_two,
             'matern32': matern32,
             'matern52': matern52}
    return bases

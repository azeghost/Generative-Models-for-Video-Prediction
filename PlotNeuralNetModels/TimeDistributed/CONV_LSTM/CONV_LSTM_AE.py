
import sys
sys.path.append('../../../')
from pycore.tikzeng import *
from pycore.blocks  import *

# defined your arch
arch = [
    to_head( '../../..' ),
    to_cor(),
    to_begin(),

    # input
    to_input('../../../pyexamples/mspacman.png'),


    # n_filer is batch size at first then batch_size * previous layers filer size from definition
    # in my case it will be batch size * EPIS_LEN since i will feed in videos
    # s_filter is inputs_shape dimentions multiplied like np.product(inputs_shape) at first later on depending on the convolution it will be different
    # inference mean
    to_Conv("conv1", s_filer=246480, n_filer=10, offset="(0,0,0)", to="(0,0,0)", height=35, depth=30, width=2 , caption="ConvLSTM2D"),
    #the hight and weight of the pool layer is depending on kernel_size=3
    to_Pool("pool1", offset="(0,0,0)", to="(conv1-east)", height=3, depth=3),

    #since my stride is (2,2) that means my dimentions will be decreased by 4 times but my intermediate dim is 30/2 so 15/3= 5
    # thus i have to multiply n_filer by 5
    to_Conv("conv2", 7956, 10, offset="(1.5,0,0)", to="(pool1-east)", height=15, depth=10, width=2 ,caption="ConvLSTM2D"),
    to_connection( "pool1", "conv2"),

    to_Pool("pool2", offset="(0,0,0)", to="(conv2-east)", height=3, depth=3, width=1),

    to_SoftMax(name="flat1", s_filer= 8400 ,offset= "(2.0,0,0)", to = "(pool2-east)", caption="Flatten",
               height=20, depth=20, width=1),
    to_connection("pool2", "flat1"),

    to_Conv(name="dense1", s_filer=2386830, n_filer=30, offset= "(2.0,0,0)", to="(flat1-east)", caption="dense1",
            height=19, depth=19, width=2),
    to_connection("flat1", "dense1"),

#     to_SoftMax(name="batchnorm1", s_filer=30, offset= "(1.5,0,0)", to="(dense1-east)", caption="batchNorm",
#             height=11, depth=11, width=2),
#     to_connection("dense1", "batchnorm1"),

#     to_SoftMax(name="dropout1",  s_filer=30, offset= "(1.5,0,0)", to="(batchnorm1-east)", caption="dropout",
#             height=9, depth=9, width=2),
#     to_connection("batchnorm1", "dropout1"),

#     to_SoftMax(name="ar1",  s_filer=30, offset= "(1.5,0,0)", to="(dropout1-east)", caption="ActReg",
#             height=7, depth=7, width=2),
#     to_connection("dropout1", "ar1"),
    
    to_SoftMax(name="inference_outputs", s_filer=30, offset="(1,0,0)", to="(dense1-east)", caption="Latents",
            height=5, depth=5, width=10),
    to_connection("dense1", "inference_outputs"),
    #
    # #inferense logvar
    # to_Conv("convb1", s_filer=100800, n_filer=300, offset="(0,-10,0)", to="(0,0,0)", height=45, depth=40, width=2 , caption="conv1"),
    # #the hight and weight of the pool layer is depending on kernel_size=3
    # to_Pool("poolb1", offset="(0,0,0)", to="(convb1-east)", height=3, depth=3),
    #
    # #since my stride is (2,2) that means my dimentions will be decreased by 4 times but my intermediate dim is 30/2 so 15/3= 5
    # # thus i have to multiply n_filer by 5
    # to_Conv("convb2", 25200, 1500, offset="(1.5,0,0)", to="(poolb1-east)", height=15, depth=13, width=2 ,caption="conv2"),
    # to_connection( "poolb1", "convb2"),
    #
    # to_Pool("poolb2", offset="(0,0,0)", to="(convb2-east)", height=3, depth=3, width=1),
    #
    # to_SoftMax(name="flatb1", s_filer= 8400 ,offset= "(2.0,0,0)", to = "(poolb2-east)", caption="Flatten",
    #            height=20, depth=20, width=1),
    # # to_Pool(name='Flatten', to),
    #
    # to_connection("poolb2", "flatb1"),
    #
    # to_Conv(name="denseb1", s_filer=238710, n_filer=30, offset= "(2.5,0,0)", to="(flatb1-east)", caption="dense1",
    #         height=19, depth=19, width=2),
    # to_connection("flatb1", "denseb1"),
    #
    # to_SoftMax(name="inference_log_outputs", s_filer=30, offset="(1,0,0)", to="(dense1-east)", caption="Latents",
    #            height=5, depth=5, width=10),
    # to_connection("denseb1", "inference_log_outputs"),

    # Decoder
    to_Conv(name='dense2', s_filer=210000, n_filer=30, offset="(1,0,0)", to="(inference_outputs-east)",
            width=5, height=10, depth=10, caption="dense2"),
    to_connection("inference_outputs", "dense2"),

    to_Conv(name='reshape', s_filer=21000, n_filer=15, offset="(1,0,0)", to="(dense2-east)",
            height=15, depth=13, width=2, caption="Reshape"),
    to_connection("dense2", "reshape"),

    to_Conv(name='deconv3', s_filer=8400, n_filer=300, offset="(1.5,0,0)", to="(reshape-east)",
            height=15, depth=13, width=4, caption="TimeDistConv2DTr1"),
    to_Pool("pool4", offset="(0,0,0)", to="(deconv3-east)", height=2, depth=3, width=1),
    to_connection("reshape", "deconv3"),

    to_Conv(name='deconv4', s_filer=160*210, n_filer=60, offset="(2,0,0)", to="(deconv3-east)",
            height=35, depth=30, width=2, caption="TimeDistConv2DTr2"),
    to_Pool("pool5", offset="(0,0,0)", to="(deconv4-east)", height=2, depth=2, width=1),
    to_connection("pool4", "deconv4"),

    to_Conv(name='deconv5', s_filer=10*160*210, n_filer=3, offset="(5,0,0)", to="(deconv3-east)",
            height=45, depth=40, width=2, caption="TimeDistConv2DTr3"),
    to_connection("pool5", "deconv5"),
    
#     to_SoftMax(name="batchnorm2", s_filer=3, offset= "(2.5,0,0)", to="(deconv5-east)", caption="batchNorm",
#             height=42, depth=40, width=2),
#     to_connection("deconv5", "batchnorm2"),

#     to_SoftMax(name="dropout2",  s_filer=3, offset= "(2.5,0,0)", to="(batchnorm2-east)", caption="dropout",
#             height=45, depth=40, width=2),
#     to_connection("batchnorm2", "dropout2"),

#     to_SoftMax(name="ar2",  s_filer=3, offset= "(2.5,0,0)", to="(dropout2-east)", caption="ActReg",
#             height=45, depth=40, width=2),
#     to_connection("dropout2", "ar2"),

    to_ConvSoftMax(name="soft1", s_filer=512, offset="(0.45,0,0)", to="(deconv5-east)",
                   width=1, height=45, depth=40, ),
    to_end()
    ]

def main():
    namefile = str(sys.argv[0]).split('.')[0]
    to_generate(arch, namefile + '.tex' )

if __name__ == '__main__':
    main()

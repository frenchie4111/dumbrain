    def loss(self, sample):
        xs = Variable(sample['xs']) # support
        xq = Variable(sample['xq']) # query

        n_class = xs.size(0) # n_class = 4
        assert xq.size(0) == n_class
        n_support = xs.size(1) 
        n_query = xq.size(1) # n_query = 2


        # target_inds
        target_inds = torch
            .arange(0, n_class)             # = [0, 1, 2, 3]
            .view(n_class, 1, 1)            # = [[[0]], [[1]], [[2]], [[3]]] // shape=( 4, 1, 1 )
            .expand(n_class, n_query, 1)    # = [ [[0], [0]], [[1], [1]], [[2], [2]], [[3], [3]] ] // Shape = 4, 2, 1
            .long()

        target_inds = Variable(target_inds, requires_grad=False)

        if xq.is_cuda:
            target_inds = target_inds.cuda()

        x = torch.cat([xs.view(n_class * n_support, *xs.size()[2:]),
                       xq.view(n_class * n_query, *xq.size()[2:])], 0)

        z = self.encoder.forward(x)
        z_dim = z.size(-1)

        z_proto = z[:n_class*n_support].view(n_class, n_support, z_dim).mean(1)
        zq = z[n_class*n_support:]

        dists = euclidean_dist(zq, z_proto)

        log_p_y = F.log_softmax(-dists).view(n_class, n_query, -1)
        # = [ [[sm0], [sm0]] ]

        loss_val = -log_p_y.gather(2, target_inds).squeeze().view(-1).mean()

        _, y_hat = log_p_y.max(2)
        acc_val = torch.eq(y_hat, target_inds.squeeze()).float().mean()

        return loss_val, {
            'loss': loss_val.data[0],
            'acc': acc_val.data[0]
        }
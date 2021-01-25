import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import time
import matplotlib.pyplot as plt

def change_lr(optimizer, lr):
    for g in optimizer.param_groups:
        g['lr'] = lr


def train(net, device, train_loader, val_loader, EPOCHS = 30, lr = 0.001):
    criterion = nn.CrossEntropyLoss().cuda()
    # lr = 0.001
    optimizer = optim.Adam(net.parameters(), lr = lr, weight_decay=1e-4, betas=(0.9, 0.999))
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, 'min', patience = 1, factor = 0.5, verbose = True)
    num_batches = len(train_loader)
    train_loss_arr = []
    val_loss_arr = []
    best_loss = 1.0
    # EPOCHS = 30
    print("Training Started at ", time.strftime("%H:%M:%S", time.localtime()))
    start = time.time()
    for epoch in range(0,EPOCHS):  # loop over the dataset multiple times
        epoch_start = time.time()
        running_loss = 0.0
        epoch_loss = 0.0
        i = 0
        net.train()
        for i, data in enumerate(train_loader, 0):
            # get the inputs; data is a list of [inputs, labels]
            inputs, labels = data[0].to(device), data[1].to(device)
            if inputs.shape[0] < 5:
                continue
    
            # zero the parameter gradients
            optimizer.zero_grad()
    
            # forward + backward + optimize
            outputs = net(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
    
            # print statistics
            running_loss += loss.item()
            epoch_loss += loss.item()
            if i != 0 and (i+1) % 300 == 0:    # print every 300 mini-batches
                print('[%d, %5d] loss: %.6f' %
                      (epoch + 1, i+1, running_loss / 300))
                running_loss = 0.0
        
        train_loss = epoch_loss/num_batches
        val_acc, val_loss = val(net, device, val_loader, criterion)
        train_loss_arr.append(train_loss)
        val_loss_arr.append(val_loss)
        print("Epoch %s complete => Train_Loss : %.6f, Val_Loss : %.6f, Val_acc : %.2f , time taken : %s"%(epoch+1, train_loss, val_loss, val_acc, time.time() - epoch_start))
    
        #SAVE Best Model
        if epoch > (EPOCHS/2) and val_loss < best_loss : 
            torch.save(net.state_dict(), 'SKNET.pt')
            print("Model saved")
    
    print("Training Finieshed at ", time.strftime("%H:%M:%S", time.localtime()))
    print("Time to train = %s seconds"%(time.time() - start))
    plt.plot(range(1, len(train_loss_arr)+1), train_loss_arr)
    plt.plot(range(1, len(val_loss_arr)+1), val_loss_arr)
    plt.legend(["train","val"])
    
    return net

def val(net, device, test_loader, criterion):
    correct = 0
    total = 0
    net.eval()
    loss = 0
    with torch.no_grad():
        for data in test_loader:
            images, labels = data[0].to(device), data[1].to(device)
            outputs = net(images)   
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
            loss += criterion(outputs, labels)
    
    accuracy = 100 * correct / total
    loss = loss / len(test_loader)
    
    return accuracy, loss.item()

def test(net, device, test_loader):
    correct = 0.0
    total = 0.0
    net.eval()
    with torch.no_grad():
        for data in test_loader:
            images, labels = data[0].to(device), data[1].to(device)
            outputs = net(images)   
            outputs = F.softmax(outputs, dim = 1)
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
    
    print('Accuracy of the network on the 10000 test images: %s %%' % (
        100 * correct / total))
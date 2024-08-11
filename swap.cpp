#include<iostream>
using namespace std;

void printarr(int arr[],int size){
    for(int i=0;i<size;i++){
        cout<<arr[i]<<" ";
    }
}

void swapele(int arr[], int size){
    for(int i=0;i<size;i+=2){
        if(i+1<size){
        swap(arr[i],arr[i+1]);
        }
        
    }
}

int main(){
    int i;
    int arr[8]={2,6,8,2,7,1,5,9} ;

    int ans[5]={3,5,8,1,9};

    //int size= arr.size();
    swapele(ans,5);
    printarr(ans,5);

    return 0;
}
// pages/my/my.js
//获取应用实例
const app = getApp()
var SocketTask;
Page({

	/**
	 * 页面的初始数据
	 */
	data: {
        final_tips:'',
        userInfo: {},
        hasUserInfo: false,
        canIUse: wx.canIUse('button.open-type.getUserInfo'),
        parking_info:false,
        che_pai_hao:'',
        canIUseGetUserProfile: false,
        canIUseOpenData: wx.canIUse('open-data.type.userAvatarUrl') && wx.canIUse('open-data.type.userNickName'), // 如需尝试获取用户信息可改为false
        hours: '0' + 0,   // 时
        minute: '0' + 0,   // 分
        second: '0' + 0,    // 秒
        loanTime:'' 
      },
    //事件处理函数
    bindViewTap: function() {
        
    },
	/**
	 * 生命周期函数--监听页面加载
	 */
	onLoad: function (options) {
       if (app.globalData.userInfo) {
            this.setData({
                userInfo: app.globalData.userInfo,
                hasUserInfo: true
            })
        } else if (this.data.canIUse){
            // 由于 getUserInfo 是网络请求，可能会在 Page.onLoad 之后才返回
            // 所以此处加入 callback 以防止这种情况
            app.userInfoReadyCallback = res => {
                this.setData({
                userInfo: res.userInfo,
                hasUserInfo: true
            })
        }
        } else {
        // 在没有 open-type=getUserInfo 版本的兼容处理
            wx.getUserInfo({
                success: res => {
                app.globalData.userInfo = res.userInfo
                this.setData({
                    userInfo: res.userInfo,
                    hasUserInfo: true
                })
                }
            })
        }
	},

	/**
	 * 生命周期函数--监听页面初次渲染完成
	 */
	onReady: function () {

	},

	/**
	 * 生命周期函数--监听页面显示
	 */
	onShow: function () {

	},

	/**
	 * 生命周期函数--监听页面隐藏
	 */
	onHide: function () {

	},

	/**
	 * 生命周期函数--监听页面卸载
	 */
	onUnload: function () {

	},

	/**
	 * 页面相关事件处理函数--监听用户下拉动作
	 */
	onPullDownRefresh: function () {

	},

	/**
	 * 页面上拉触底事件的处理函数
	 */
	onReachBottom: function () {

	},

	/**
	 * 用户点击右上角分享
	 */
	onShareAppMessage: function () {

    },
    getUserInfo: function(e) {
        console.log(e)
        app.globalData.userInfo = e.detail.userInfo
        this.setData({
          userInfo: e.detail.userInfo,
          hasUserInfo: true
        })
    },
    saoMa: function() {
        var that = this
        this.webSocket()
        setTimeout(function () {
          SocketTask.send({
            data: "saoma"
          }, function (res) {
            console.log('已发送', res)
          })
         }, 1000) //延迟时间 这里是1秒
        wx.scanCode({
          onlyFromCamera: true,//仅仅相机
          success: (res) => {
            if(res.result==String("https://u.wechat.com/EPA2tpHjYRl1J1MXmix3r0w"))
            {
              that.setData({
                final_tips:"停车成功",
                parking_info:true
              })
            }
            else
            {
              that.setData({
                final_tips:"扫码失败",
                parking_info:false
              })
            }
          },
          //错误返回
          fail: (res) => {
            wx.showToast({
              title: '扫码失败',
              icon: 'none',
              duration: 1000,
            })
            that.setData({
              parking_info:false
            })
          },
          complete: function (res) {
            SocketTask.send({
              data: "saoma_wancheng"
            }, function (res) {
              console.log('已发送', res)
            })
            wx.onSocketMessage(function(res){
              that.setData({
                che_pai_hao:res.data,
              })
            })
            setTimeout(function () {
             wx.closeSocket()   
             }, 1500)
            console.log("正在断开树莓派的连接")
            that.setInterval()
            wx.showToast({
              title:that.data.final_tips,
              icon: 'none',
              duration: 2000
            })
           
           },
        })
      },

      li_kai:function(){
        this.webSocket()
        setTimeout(function () {
          SocketTask.send({
            data: "likai"
          }, function (res) {
            console.log('已发送', res)
          })
         }, 1000)
         this.setData({
          parking_info:false
         })
         wx.showToast({
          title:"已取消当前停车位占用",
          icon: 'none',
          duration: 2000
        })
        setTimeout(function () {
          wx.closeSocket()   
          }, 1500)
      },

      webSocket: function () {    
        // 创建Socket    
        SocketTask = wx.connectSocket({      
          url: 'ws://ip:8000',
          header: {        
            'content-type': 'application/json'      
          },
          method: 'post',
          success: function (res) {       
             console.log('WebSocket连接创建', res)        
            },
            fail: function (err) {        
              wx.showToast({          
                title: '网络异常！',
                })        
                console.log(err)      
              },
          })  
      },
      setInterval: function () {
        const that = this
        that.setData({
          second:Math.floor(Math.random()*10 + 30),
          minute:0,
          hours:0
        })
        var second = that.data.second
        var minute = that.data.minute
        var hours = that.data.hours
        clearInterval(that.data.loanTime)      
        that.data.loanTime=setInterval(function () {  // 设置定时器
            second++
            if (second >= 60) {
                second = 0  //  大于等于60秒归零
                minute++
                if (minute >= 60) {
                    minute = 0  //  大于等于60分归零
                    hours++
                    if (hours < 10) {
                        // 少于10补零
                        that.setData({
                            hours: '0' + hours
                        })
                    } else {
                        that.setData({
                            hours: hours
                        })
                    }
                }
                if (minute < 10) {
                    // 少于10补零
                    that.setData({
                        minute: '0' + minute
                    })
                } else {
                    that.setData({
                        minute: minute
                    })
                }
            }
            if (second < 10) {
                // 少于10补零
                that.setData({
                    second: '0' + second
                })
            } else {
                that.setData({
                    second: second
                })
            }
        }, 1000)
    }
})
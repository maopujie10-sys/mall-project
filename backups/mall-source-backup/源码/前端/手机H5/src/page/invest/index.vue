<template>
  <div class="invest">
    <div>

    </div>
    <van-nav-bar safe-area-inset-top
        fixed

        :title="$t('我要投资')"
    />
    <div style="width: 100%;" class="h46"></div>
    <van-tabs v-model="active" @click="qiehuan" style="position: fixed;z-index: 999;" class="pw1">

      <van-tab v-for="(item,index) in project_listCategory" :key="index" :title="item.name" :name="item.baseId"></van-tab>

    </van-tabs>
    <div style="width: 100%;" class="h44"></div>
    <div class="padd-15">
      <van-pull-refresh style="min-height: 100vh;" v-model="refreshing" @refresh="onRefresh" :pulling-text="$t('下拉即可刷新')" :loosing-text="$t('释放即可刷新')" :loading-text="$t('加载中')">
        <van-list
            v-model="loading"
            :finished="finished"
            :loading-text="$t('加载中')"
            :finished-text="$t('没有更多了')"
            @load="onLoad"
        >
      <div v-for="(item,index) in list" :key="index" @click="touzi(item.projectId)" class="touzi-xm">
        <div class="xm-title">
          <div class="van-multi-ellipsis--l2">
            {{ item.name }}
          </div>

        </div>
        <div class="xm-xinxi">
          <div class="xinxi-k1">
            <div class="k-n">{{ item.investMin }}</div>
            <div class="k-title">Starting amount</div>
          </div>
          <div class="xinxi-k1">
            <div class="k-n">{{ (item.bonusRate * 100).toFixed(2) }}%</div>
            <div class="k-title">Daily Returns</div>
          </div>
          <div class="xinxi-k2">
<!--            <div class="k-n">1000.00</div>-->
            <div class="k-n" v-if="item.type <3">{{ item.bonus }}{{ $t('小时') }}</div>
            <div class="k-n" v-else>{{ item.bonus }}{{ $t('天') }}</div>
            <div class="k-title">Project Period</div>
          </div>
        </div>
        <div class="jindu">
          <div style="flex: 1;margin-right: 15px;">
            <div class="jindu-t">
              <div :class="item.isSellOut==1?'xuanzhong2':'xuanzhong'"
                   :style="'width:'+(item.progress*100).toFixed(2)+'%'"></div>
            </div>
            <div class="jindu-title">
              <div class="t1">Progress</div>
              <div class="t2">{{ (item.progress * 100).toFixed(2) }}%</div>
            </div>
          </div>
          <div class="tj" :class="item.isSellOut==1?'tj-hui':'tj-lan'">

            {{item.isSellOut==1?$t('已售完'):$t('立即参与')}}
          </div>
        </div>
      </div>
        </van-list>
      </van-pull-refresh>
    </div>
    <div style="width: 100%;" class="h90"></div>
  </div>
</template>
<script>
import {NavBar, Tab, Tabs,PullRefresh,List} from 'vant';
import {project_listCategory_action_post, project_listProject_action_post, wodetuandui_post} from "@/API/user";

export default {
  data() {
    return {
      active: '',
      project_listCategory:[],
      list: [],
      loading: false,
      finished: false,
      refreshing: false,
      page_no: 0,
    }
  },
  components: {
    [NavBar.name]: NavBar,
    [Tab.name]: Tab,
    [Tabs.name]: Tabs,
    [List.name]: List,
    [PullRefresh.name]: PullRefresh,
  },
  created() {
    this.project_listCategory_action()
  },
  methods: {
    onRefresh() {
      // 清空列表数据
      this.finished = false;
      this.page_no = 0
      // 重新加载数据
      // 将 loading 设置为 true，表示处于加载状态
      this.loading = true;
      this.onLoad();
    },
    onLoad() {
      if (this.refreshing) {
        this.list = [];
        this.refreshing = false;
      }
      this.tuanduimingxi_post()
    },
    tuanduimingxi_post() {
      this.page_no++
      var data = {
        'pageNum': this.page_no,
        'pageSize': 10,
        'baseId': this.active,
      }
      project_listProject_action_post(data).then(res => {
        console.log(res)
        for (let i = 0; i < res.pageList.length; i++) {
          this.list.push(res.pageList[i]);
        }
        console.log(this.list)
        this.loading = false;

        if (res.pageList.length == 0) {
          this.finished = true;
        }
      })
    },
    qiehuan() {
      this.list = [];
      this.loading = false;
      this.finished = false;
      this.refreshing = false;
      this.page_no = 0;
      document.body.scrollTop = 0
      // firefox
      document.documentElement.scrollTop = 0
      // this.onLoad()
    },
    project_listCategory_action(){
      project_listCategory_action_post({}).then(res=>{
        console.log(res.pageList)
        this.project_listCategory = res.pageList
        if (res.pageList.length!==0){
          this.active = res.pageList[0]['baseId']
        }
        this.qiehuan()
      })
    },
    touzi(e) {
      document.body.scrollTop = 0
      // firefox
      document.documentElement.scrollTop = 0
      this.$router.push('/ProductDetails?projectId='+e)
    },
    onClickLeft() {
      this.$router.push('/me')
    },
  }
}
</script>
<style lang="scss" scoped>
.invest {
  position: relative;
  background: #EFF2F7;
  min-height: 100%;
  .pw1{
    width: 375px;
  }

  .padd-15 {
    padding: 0 15px;
    box-sizing: border-box;
  }

  .touzi-xm {
    margin-top: 15px;
    background: #FFFFFF;
    border-radius: 4px;
    padding: 15px;
    box-sizing: border-box;
    width: 100%;

    .xm-title {
      font-style: normal;
      font-weight: 600;
      font-size: 16px;

      color: #000000;

    }

    .xm-xinxi {
      margin-top: 15px;
      display: flex;

      .k-n {
        font-style: normal;
        font-weight: 400;
        font-size: 18px;
        /* identical to box height */
        color: #333333;
        //text-align: center;
      }

      .k-title {
        font-style: normal;
        font-weight: 400;
        font-size: 12px;
        //line-height: 14px;
        /* identical to box height */

        //text-align: center;

        color: #999999;
      }

      .xinxi-k1 {
        flex: 1;
      }
    }

    .jindu {
      margin-top: 15px;
      width: 100%;
      display: flex;
      justify-content: center;
      align-items: flex-start;

      .jindu-t {
        margin-top: 2px;
        width: 140px;
        height: 8px;
        background: #EEEEEE;
        border-radius: 27px;

        .xuanzhong {
          height: 8px;
          background: #1552F0;
          border-radius: 27px;
        }

        .xuanzhong2 {
          height: 8px;
          background: #999999;
          border-radius: 27px;
        }
      }

      .jindu-title {
        width: 140px;
        margin-top: 8px;
        display: flex;
        justify-content: space-between;

        .t1 {
          font-style: normal;
          font-weight: 400;
          font-size: 12px;
          color: #000000;
        }

        .t2 {
          font-style: normal;
          font-weight: 400;
          font-size: 12px;
          color: #000000;
        }
      }

      .tj {
        width: 96px;
        height: 36px;
        font-style: normal;
        font-weight: 400;
        font-size: 14px;
        line-height: 36px;
        /* identical to box height, or 114% */

        text-align: center;

        color: #FFFFFF;


        border-radius: 4px;
      }

      .tj-lan {
        background: #1552F0;
      }

      .tj-hui {
        background: #999999;
      }
    }
  }
}
</style>
<style>
.invest [class*=van-hairline]::after {
  border: none;
}
</style>

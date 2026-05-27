<template>
  <div class="merchandise promotion">
    <SetBootSteps/>
    <el-card>
      <div class="main-top">
        <div class="mb-30 ">
          <p style="font-size: 14px; margin-bottom: 10px">{{ $t('邀请链接') }}</p>
          <div class="flex justify-between w-591 rounded-md link-main">
            <p class="linkA">{{ promotional.download + '/#/?usercode=' + promotional.code }}</p>
            <el-button :data-clipboard-text="promotional.download+'/#/?usercode='+promotional.code" class="tag-read"
                       type="primary" @click="copy(promotional.download+'/#/?usercode='+promotional.code)">{{
                $t('复制')
              }}
            </el-button>
          </div>
        </div>
        <div>
          <p style="font-size: 14px; margin-bottom: 10px">{{ $t('邀请码') }}</p>
          <div class="flex justify-between w-591 rounded-md link-main">
            <p class="linkA">{{ promotional.code }}</p>
            <el-button :data-clipboard-text="promotional.code" class="tag-read" type="primary"
                       @click="copy(promotional.code)">
              {{ $t('复制') }}
            </el-button>
          </div>
        </div>
      </div>
    </el-card>
    <el-card>
      <div class="main-top">
        <div class="mb-20">
          <span
              v-html="$t('成为创业联盟会员后，您可以邀请好友通过您的邀请码进行注册。每当您的好友在我们平台上完成一笔订单，您就能获得相应的佣金奖励。根据您邀请的好友层数，您可以获得不同比例的分成。')">
          </span>
          <span
              v-html="$t('一级好友的商品销售利润将给您{_$1}的分成，',{_$1:'<span class=tip>'+((promotional.promoRate1||0)*100).toFloor(0)+'%</span>'})"></span>
          <span
              v-html="$t('二级好友的商品销售利润将给您{_$1}的分成，',{_$1:'<span class=tip>'+((promotional.promoRate2||0)*100).toFloor(0)+'%</span>'})"></span>
          <span
              v-html="$t('三级好友的商品销售利润将给您{_$1}的分成。',{_$1:'<span class=tip>'+((promotional.promoRate3||0)*100).toFloor(0)+'%</span>'})"></span>
        </div>
        <div class="mb-12" v-html="$t('以下是分成计算公式：')" style="margin-top: 12px;"></div>
        <div
            v-html="$t('一级好友分成计算公式：佣金 = 商品销售利润 x {_$1}',{_$1:'<span class=tip>'+((promotional.promoRate1||0)*100).toFloor(0)+'%</span>'})"></div>
        <div
            v-html="$t('二级好友分成计算公式：佣金 = 商品销售利润 x {_$1}',{_$1:'<span class=tip>'+((promotional.promoRate2||0)*100).toFloor(0)+'%</span>'})"></div>
        <div class="mb-20"
             v-html="$t('三级好友分成计算公式：佣金 = 商品销售利润 x {_$1}',{_$1:'<span class=tip>'+((promotional.promoRate3||0)*100).toFloor(0)+'%</span>'})"></div>
        <div class="mb-20"
             v-html="$t('我们提供详细的分成计算公式，以便您清晰了解佣金的计算方式。我们鼓励您了解平台的邀请制度规则，以便更好地管理和规划您的佣金收入。我们感谢您的参与，并期待与您共同发展。')"></div>
      </div>
    </el-card>
    <el-card>
      <el-tabs v-model="activeName" @tab-click="tab">
        <el-tab-pane v-for="(item, index) in tabList" :key="item.key" :label="item.label" :name="item.key">
          <div class="tab-main" style="min-height: 250px;position: relative;padding-bottom: 36px;">
            <template v-if="tableData.length>0">
              <div v-for="(item, index) in tableData" :key="index" class="tab-b">
                <img :src="item.avatar" alt="" class="w-44 h-44 mr-15"
                     style="border-radius: 50%;display: block;"/>
                <div>
                  <p style="font-weight: bold; margin-bottom: 5px; font-size: 14px">
                    {{ item.name }}
                  </p>
                  <div><span style="margin-bottom: 5px">{{ $t('收益') }}</span>: {{ (item.income || 0).toFloor(2) }}
                  </div>
                  <div>
                    <span style="margin-right: 100px">{{ $t('订单') }}: {{ item.orderCount || 0 }}</span>
                    <span>{{ $t('注册日期') }}: {{ item.createTime }}</span>
                  </div>
                </div>
              </div>
            </template>
            <div class="noData" v-else
                 style="display: flex;flex-direction: column;align-items: center;justify-content: center;width: 100%;height: 250px;">
              <el-image :src="empty" style="height: 120px;margin-bottom: 12px"/>
              {{ $t("暂无记录") }}
            </div>
            <div
                style="margin-top: 20px; text-align: center;position: absolute;width: 100%;display: flex;justify-content: center;bottom: 0;">
              <el-row>
                <el-button size="mini" @click="fenye('b')">{{ $t("上一页") }}</el-button>
                <el-button size="mini" style="margin-left: 10px;" @click="fenye('a')">
                  {{ $t("下一页") }}
                </el-button>
              </el-row>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script>
import Clipboard from 'clipboard';
import {promotional_post, promotional_team_level_post} from "@/api/user";

export default {
  name: "promotion",
  data() {
    return {
      currentPage: 0,
      activeName: '1',
      empty: require('@/assets/empty-image-default.png'),
      tabList: [
        {
          label: this.$t('一级好友'),
          key: '1',
        },
        {
          label: this.$t('二级好友'),
          key: '2',
        },
        {
          label: this.$t('三级好友'),
          key: '3',
        }
      ],
      tableData: [],
      promotional: {},
      pageNum: 1,
      pageSize: 10,
    };
  },
  mounted() {
    this.promotional_post_get()
    this.promotional_team_level()
  },
  methods: {
    fenye(x) {
      if (x == 'a') {
        this.pageNum++
      }
      if (x == 'b') {
        if (this.pageNum == '1') {
          return
        }
        this.pageNum--
      }
      this.promotional_team_level()
    },
    promotional_team_level() {
      var form = {
        level: this.activeName,
        pageNo: this.pageNum,
        pageSize: this.pageSize
      }
      promotional_team_level_post(form).then((e) => {
        console.log(e)
        this.tableData = e.data || []
      })
    },
    promotional_post_get() {
      promotional_post({}).then((e) => {
        console.log(e)
        this.promotional = e.data
      })
    },
    tab() {
      this.pageNum = 1
      this.promotional_team_level()
    },
    // TODO: 每页几条,去请求获取数据
    handleSizeChange(val) {
      console.log(`每页 ${val} 条`);
      this.getAllData();
    },
    // TODO: 当前第几页,去请求获取数据
    handleCurrentChange(val) {
      console.log(`当前页: ${val}`);
      this.getAllData();
    },
    copy() {
      var clipboard = new Clipboard('.tag-read')
      clipboard.on('success', e => {
        console.log('复制成功')
        this.$message.success(this.$t('复制成功'))
        // 释放内存
        clipboard.destroy()
      })
      clipboard.on('error', e => {
        // 不支持复制
        console.log('该浏览器不支持自动复制')
        // 释放内存
        clipboard.destroy()
      })
    }
  }
};
</script>

<style lang="scss" scoped>
.merchandise {
  background-color: #f0f2f5;
  padding: 20px;
  // height: 100%;
  .main {
    padding: 20px;
    background-color: #fff;
    margin-bottom: 10px;
    border-radius: 10px;

    .main-top {
      //display: flex;
      margin-bottom: 30px;
    }

    .linkA {
      font-size: 14px;
      padding: 12px 10px;
    }

    .tab-main {


    }

  }

  .noData {
    font-size: 14px;
  }

}

.tab-b {
  display: flex;
  border-bottom: 1px solid #f0f2f5;
  font-size: 13px;
  color: #666666;
  display: flex;
  align-items: center;
  padding: 6px 12px;
}

.link-main {
  border: 1px solid #DCDFE6;
  line-height: 34px;
  text-indent: 12px;
  position: relative;
  box-sizing: border-box;
}

.tag-read {
  position: absolute;
  right: -1px;
  top: -1px;
  border-top-left-radius: 0;
  border-bottom-left-radius: 0;
}
</style>
<style lang="scss">
.main-top {
  .tip {
    color: rgb(245, 108, 108);
  }
}
</style>



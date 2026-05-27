<template>
  <div class="merchandise">
    <div class="main">
      <p>{{ $t('产品') }}</p>
      <div class="main-t">
        <div class="main-b bg">
          <img alt="" src="@/assets/images/users/上传.png" style="height: 50px; width: 40px"/>
          <p style="margin: 10px 0; font-weight: bold; font-size: 18px">0</p>
          <p style="font-size: 12px">{{ $t('剩余上传') }}</p>
        </div>
        <div class="main-b co">
          <img alt="" src="@/assets/images/users/添加.png" style="height: 70px; width: 70px"/>
          <p style="margin-top: 10px">{{ $t('产品') }}</p>
        </div>
        <div class="main-b co">
          <img alt="" src="@/assets/images/users/哭脸.png" style="height: 50px; width: 50px"/>
          <p style="margin-bottom: 5px; font-size: 14px">{{ $t('未找到包裹') }}</p>
          <p style="
                                                                            font-size: 14px;
                                                                            border: 1px solid #e98f36;
                                                                            width: 100px;
                                                                            height: 30px;
                                                                            margin: 0 auto;
                                                                            border-radius: 5px;
                                                                            line-height: 30px;
                                                                          ">{{ $t('升级包') }}</p>
        </div>
      </div>
      <div class="main-main">
        <p class="all">{{ $t('产品') }}</p>
        <div class="main-tb">
          <el-table ref="multipleTable" :data="tableData" stripe style="width: 100%; height: 400px">
            <template slot="empty">
              <div style="margin-top: 100px; font-size: 20px; color: #000">
                <img alt="" src="@/assets/images/users/哭脸 (1).png"/>
                <div>{{ $t('什么都没找到') }}</div>
              </div>
            </template>
            <el-table-column align="center" label="#" width="80"></el-table-column>
            <el-table-column :label="$t('名称')" align="center" prop="buyTime"></el-table-column>
            <el-table-column :label="$t('价格')" align="center" prop="endTime" width="200"></el-table-column>
            <el-table-column :label="$t('状态')" align="center" prop="buy_type"></el-table-column>
            <el-table-column :label="$t('状态')" align="center" prop="change_after"></el-table-column>
            <el-table-column :label="$t('选项')" align="center" prop="change_after"></el-table-column>
          </el-table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "categoryProducts",
  data() {
    return {
      tableData: []
    };
  },
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
    border: 1px solid rgba(215, 215, 215, 1);

    .main-t {
      margin: 30px 0;
      text-align: center;
      display: flex;
      justify-content: space-between;

      .main-b {
        width: 32%;
        border-radius: 5px;
        color: #fff;
        height: 130px;
        padding: 10px 0;
      }

      .co {
        color: #e98f36;
        font-size: 18px !important;
        border: 1px solid rgba(215, 215, 215, 1);
      }

      .bg {
        background-image: linear-gradient(
                to right,
                rgb(184, 84, 166),
                rgb(228, 73, 139)
        );
      }
    }

    .main-main {
      border: 1px solid rgba(215, 215, 215, 1);

      .all {
        height: 50px;
        line-height: 50px;
        padding-left: 50px;
        border-bottom: 1px solid rgba(215, 215, 215, 1);
      }

      .main-tb {
        padding: 20px;
      }
    }
  }
}
</style>

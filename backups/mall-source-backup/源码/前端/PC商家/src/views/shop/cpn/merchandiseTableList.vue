<template>
  <div class="table-list">
    <el-card>
      <el-form ref="searchForm" :model="form" inline>
        <el-form-item :label="$t('商品名称')" prop="name">
          <el-input v-model="form.name" :placeholder="$t('请输入商品名称')"></el-input>
        </el-form-item>
        <el-form-item :label="$t('商品ID')" prop="id">
          <el-input v-model="form.id" :placeholder="$t('请输入商品ID')"></el-input>
        </el-form-item>
        <el-form-item :label="$t('商品分类')" prop="categoryId">
          <GoodsCategory v-model="form.categoryId" @getCategory="getCategory"/>
        </el-form-item>
        <el-form-item :label="$t('商品状态')" prop="isShelf">
          <el-select v-model="form.isShelf" :placeholder="$t('请选择')">
            <el-option v-for="item in status_options" :key="item.value" :label="item.label" :value="item.value">
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="search">{{ $t('查询') }}</el-button>
        </el-form-item>
        <el-form-item>
          <el-button @click="reset">{{ $t('重置') }}</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    <el-card>
      <div class="btn">
        <el-button type="primary" @click="showBatch($t('批量上架'),1)"
        >{{ $t('批量上架') }}
        </el-button>
        <el-button type="danger" @click="showBatch($t('批量下架'),0)"
                   v-if="!['JustShop','FamilyShop'].includes(setting.projectTitle)"
        >{{ $t('批量下架') }}
        </el-button>
        <el-button
            type="primary"
            @click="batchEdit($t('批量修改'))"
        >
          {{ $t('批量修改') }}
        </el-button>
        <el-button type="danger" v-if="![].includes(setting.projectTitle)"
                   @click="showBatch2($t('批量删除'))"
        >
          {{ $t('批量删除') }}
        </el-button>

      </div>
      <el-table ref="multipleTable" :data="tableData"
                :selection="selection"
                border stripe style="width: 100%"
                @selection-change="handleSelectionChange">
        <el-table-column type="selection" width="55"></el-table-column>
        <el-table-column :label="$t('商品ID')" align="center" prop="id"></el-table-column>
        <el-table-column :label="$t('封面图')" align="center" prop="order_no">

          <template slot-scope="scope">
            <el-image :src="scope.row.imgUrl1"/>
          </template>

        </el-table-column>
        <el-table-column :label="$t('商品名称')" align="center" prop="name" min-width="260"></el-table-column>
        <el-table-column :label="$t('分类')" align="center" prop="categoryName">
        </el-table-column>
        <el-table-column :label="$t('二级分类')" align="center" prop="secondaryCateName">
        </el-table-column>
        <el-table-column :label="$t('采购价格')" align="center" prop="systemPrice">
          <template slot-scope="scope">
            <span style="color: #409EFF;">
              <FormatNumberShow :data="scope.row.systemPrice" :currency="true"/>
            </span>
          </template>
        </el-table-column>
        <el-table-column :label="$t('标签')" :min-width="columnWidth" align="center"
                         prop="time">
          <template slot-scope="scope">
            <!--            {{row.isShelf}}-->
            <!--            {{scope.row.isShelf}}-->
            <div class="merchandise-label">
              <div class="merchandise-label-item left">
                <div class="up en" v-if="![].includes(setting.projectTitle)">{{
                    $t('上架')
                  }}:
                </div>
                <div class="up en">{{ $t('推荐') }}:</div>
                <div class="up en">{{ $t('直通车') }}:</div>
              </div>
              <div class="merchandise-label-item">
                <div class="button" v-if="![].includes(setting.projectTitle)">
                  <el-switch v-model="scope.row.isShelf" :active-value="1" :inactive-value="0"
                             active-color="#13ce66" inactive-color="#ff4949" @change="api_goods_update(scope.row)">
                  </el-switch>
                </div>
                <div class="button">
                  <el-switch v-model="scope.row.recTime" :active-value="1" :inactive-value="0"
                             active-color="#13ce66" inactive-color="#ff4949" @change="api_goods_update(scope.row)">
                  </el-switch>
                </div>
                <div class="button">
                  <el-switch v-model="scope.row.isCombo" :active-value="1" :inactive-value="0"
                             active-color="#13ce66" inactive-color="#ff4949" @change="api_goods_update(scope.row)">
                  </el-switch>
                </div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column :label="$t('销售价格')" align="center" prop="sellingPrice">
          <template slot-scope="scope">
            <span style="color: #409EFF;">
              <FormatNumberShow :data="scope.row.sellingPrice" :currency="true"/>
            </span>
          </template>
        </el-table-column>
        <el-table-column :label="$t('折扣价')" align="center" prop="discountPrice">
          <template slot-scope="scope">
            <span v-if="scope.row.discountPrice" style="color: #409EFF;">
              <FormatNumberShow :data="scope.row.discountPrice" :currency="true"/>
            </span>
            <span v-else>{{ '--' }}</span>
          </template>
        </el-table-column>
        <el-table-column :label="$t('利润')" align="center" prop="change_money">
          <template slot-scope="scope">
            <div
                :style="{ color: ((scope.row.sellingPrice - scope.row.systemPrice) || 0) > 0 ? '#409EFF' : '#F56C6C' }">
              <!--              ${{-->
              <!--                goodsPorfit((scope.row.discountPrice ? scope.row.discountPrice : scope.row.sellingPrice), scope.row.systemPrice)-->
              <!--              }}-->
              <FormatNumberShow
                  :data="goodsPorfit((scope.row.discountPrice ? scope.row.discountPrice : scope.row.sellingPrice), scope.row.systemPrice)"
                  :currency="true"/>
            </div>
          </template>
        </el-table-column>
        <el-table-column :label="$t('累计销量')" align="center" prop="soldNum"></el-table-column>

        <!--        <el-table-column-->
        <!--          label="累计销售金额"-->
        <!--          align="center"-->
        <!--          prop="change_before"-->
        <!--        ></el-table-column>-->
        <el-table-column :label="$t('操作')" :width="columnWidth" align="center">
          <template slot-scope="scope">
            <div style="display: flex;justify-content: center;">
              <el-button @click="xiugai(scope.row)">{{ $t('修改') }}</el-button>
              <el-button type="danger" v-if="![].includes(setting.projectTitle)"
                         @click="delVisible = true,shachu=[],shachu=[scope.row.id]">{{ $t('删除') }}
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
      <div style="margin-top: 20px; text-align: center">
        <!--        <el-pagination background @size-change="handleSizeChange" @current-change="handleCurrentChange"-->
        <!--                       :current-page="form.pageNum" :page-size="form.pageSize"-->
        <!--                       layout="total, sizes, prev, pager, next, jumper" :total="form.totalElements">-->
        <!--        </el-pagination>-->
        <!--        {{form.totalElements}}-->
        <el-pagination
            :current-page.sync="form.pageNum"
            :page-size="form.pageSize"
            :total="form.totalElements"
            background
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange">
        </el-pagination>
      </div>
    </el-card>

    <el-dialog :title="$t('删除提示')" :visible.sync="delVisible" width="450px">
      <p><span>{{ $t('确认要删除吗') }}</span><span>?</span></p>
      <span slot="footer" class="dialog-footer">
        <el-button type="primary" @click="api_order_listGoods_delete(shachu,true)">
          {{ $t('确定') }}
        </el-button>
        <el-button @click="delVisible = false">{{ $t('取消') }}</el-button>
      </span>
    </el-dialog>

    <el-dialog :title="batchTitle" :visible.sync="batchVisible" width="450px">
      <p>
        <span>{{ $t('确定') }}</span>
        {{ batchTitle }}
        <span style="color: red">{{ shachu.length }}</span><span>{{ $t('个商品吗') }}</span>
      </p>
      <span slot="footer" class="dialog-footer">
        <el-button type="primary" @click="api_order_listGoods_delete(shachu)">{{
            $t('确定')
          }}</el-button>
        <el-button @click="batchVisible = false,shachu=[]">{{ $t('取消') }}</el-button>
      </span>
    </el-dialog>
    <EditCommodity ref="editCommodity" @submitCommodity="submitCommodity"/>
  </div>
</template>

<script>
import {
  api_goods_shelfBatch_post,
  api_goods_update_post,
  api_goods_update_posts,
  api_order_listGoods_delete_post,
  seller_goods_list_action_post,
  seller_info_action_post
} from "@/api/user";
import Toast from "@/utils/toast";
import {Notification} from "element-ui";
import EditCommodity from "@/components/EditCommodity";
import FormatNumberShow from "@/components/FormatNumberShow/index.vue";
import GoodsCategory from "@/components/GoodsCategory/index.vue";
import setting from "@/settings";

export default {
  name: "table-list",
  components: {GoodsCategory, FormatNumberShow, EditCommodity},

  data() {
    return {
      form: {
        categoryId: undefined,
        isShelf: undefined,
        name: undefined,
        id: undefined,
        pageNum: 1,
        pageSize: 10,
        totalElements: 0
      },
      delVisible: false,
      count: 0,
      batchTitle: '',
      batchVisible: false,
      currentPage: 0,
      status_options: [
        {
          label: this.$t('全部'),
          value: undefined,
        },
        {
          label: this.$t('上架'),
          value: "1",
        },
        {
          label: this.$t('下架'),
          value: "0",
        },
      ],
      order_options: [
        {
          label: this.$t('全部'),
          value: "all",
        },
        {
          label: this.$t('服装'),
          value: "add",
        },
        {
          label: this.$t('数码'),
          value: "remove",
        },
      ],
      tableData: [],
      selection: [],
      pageNum: 1,
      pageSize: 10,
      shachu: [],
      multipleSelection: [],
      commodityInfo: {},
      info: {},
      categoryList: [],
      promotional: {},
      selectIdObj: {//选中的id
      }
    };
  },
  computed: {
    setting() {
      return setting
    },
    columnWidth() {
      let width = 120;
      switch (this.$i18n.locale) {
        case 'en':
          width = 220;
          break;
        case 'cn':
          width = 180;
          break;
        case 'tw':
          width = 150;
          break;
        case 'de':
          width = 270;
          break;
        case 'fr':
          width = 260;
          break;
        case 'ja':
          width = 260;
          break;
        case 'ko':
          width = 220;
          break;
        case 'ms':
          width = 240;
          break;
        case 'th':
          width = 160;
          break;
        case 'pt':
          width = 250;
          break;
        case 'es':
          width = 220;
          break;
        case 'ru':
          width = 250;
          break;
        case 'el':
          width = 220;
          break;
        case 'it':
          width = 250;
          break;
        case 'tr':
          width = 250;
          break;
        case 'af':
          width = 250;
          break;
        case 'ph':
          width = 250;
          break;
        case 'ar':
          width = 190;
          break;
        case 'vi':
          width = 250;
          break;
        case 'id':
          width = 250;
          break;
        case 'hi':
          width = 180;
          break;
      }
      return width;
    },
  },
  mounted() {
    this.seller_info_action()
  },
  methods: {
    //根据商品id获取商品信息
    getCategory(res) {
      this.categoryList = res;
    },
    goodsPorfit(number1, number2) {
      let profit = this.$bigDecimal.subtract(number1, number2)
      return (profit * 1).toFloor(2)
    },
    seller_info_action() {
      seller_info_action_post({}).then((e) => {
        this.info = e.data
        this.seller_goods_list_action()
      }).catch((e) => {
      })
    },
    xiugai(e) {
      this.goodsIds = e.goodsIds
      this.commodityInfo = JSON.parse(JSON.stringify(e))
      this.commodityInfo.profitRatio = e.profitRatio * 100
      this.commodityInfo.discountRatio = e.discountRatio ? this.$bigDecimal.multiply(e.discountRatio, 100) : ''
      this.commodityInfo.shoujia = this.$bigDecimal.subtract((e.discountPrice ? e.discountPrice : e.sellingPrice), e.systemPrice)
      this.commodityInfo.shoujia2 = e.sellingPrice
      // scope.row.discountPrice ? scope.row.discountPrice : scope.row.sellingPrice) - scope.row.systemPrice
      // this.commodityInfo.sellingPrice = ''
      this.$refs.editCommodity.changeEditVisible(true)
      this.$refs.editCommodity.changeUpdateInfo(this.commodityInfo)
    },
    editVisibleClose() {
      this.commodityInfo.profitRatio = this.$bigDecimal.divide(this.commodityInfo.profitRatio, 100)
    },
    showBatch2(title) {
      this.count = this.$refs.multipleTable.selection.length
      this.batchTitle = title
      this.shachu = []
      if (this.multipleSelection.length == 0) {
        Toast(this.$t('请选择商品'));
        return;
      }
      for (let i = 0; i < this.multipleSelection.length; i++) {
        this.shachu.push(this.multipleSelection[i].id)
      }
      this.batchVisible = true
    },
    batchEdit(title) {
      this.count = this.$refs.multipleTable.selection.length
      this.batchTitle = title
      this.editList = []
      if (this.multipleSelection.length == 0) {
        Toast(this.$t('请选择商品'));
        return;
      }
      for (let i = 0; i < this.multipleSelection.length; i++) {
        this.editList.push(this.multipleSelection[i].id)
      }
      this.goodsIds = this.editList.join(',')
      this.$refs.editCommodity.changeEditVisible(true)
      this.$refs.editCommodity.changeUpdateInfo(null, 1)
      this.$refs.editCommodity.reset();
    },
    submitCommodity(e) {
      if (e.profitRatio === '' || e.profitRatio === null) {
        Notification.warning({
          title: this.$t('提示'),
          message: this.$t('请输入利润比例')
        })
        return
      }
      let form = {
        percent: e.profitRatio ? e.profitRatio / 100 : 0,
        isShelf: e.isShelf,
        recTime: e.recTime,
        isCombo: e.isCombo ?? 0,
        discount: e.discountRatio ? e.discountRatio / 100 : 0,
        startTime: e.discountStartTime,
        endTime: e.discountEndTime,
        sellerGoodsId: e.id ? e.id : this.goodsIds
      }
      if (e.id) {
        api_goods_update_post(form).then((e) => {
          this.editVisible = false
          this.$refs.editCommodity.changeEditVisible(false)
          Toast.success(this.$t('修改成功'));
          this.$refs.multipleTable.clearSelection()
          this.getAllData()
        })
      } else {
        api_goods_update_posts(form).then((e) => {
          this.editVisible = false
          this.$refs.editCommodity.changeEditVisible(false)
          Toast.success(this.$t('修改成功'));
          this.$refs.multipleTable.clearSelection()
          this.getAllData()
        })
      }

    },
    handleSelectionChange(val) {
      this.$nextTick(() => {
        //清除所有选中的项目
        this.tableData.forEach(item => {
          this.selectIdObj[item.id] = 0;
        })
        val.forEach(item => {
          this.selectIdObj[item.id] = 1;
        })

        this.multipleSelection = val;
      });
    },
    showBatch(title, type) {
      this.count = this.$refs.multipleTable.selection.length
      this.batchTitle = title
      // this.batchVisible = true
      // console.log(this.$refs.multipleTable.selection);
      this.shachu = []
      if (this.multipleSelection.length == 0) {
        Toast(this.$t('请选择商品'));
        return;
      }
      for (let i = 0; i < this.multipleSelection.length; i++) {
        this.shachu.push(this.multipleSelection[i].id)
      }
      this.batchVisible = true
    },
    api_order_listGoods_delete(e, deleteFlag) {
      if (this.batchTitle == this.$t('批量删除') || deleteFlag) {
        let form = {
          sellerGoodsId: e.toString()
        }
        api_order_listGoods_delete_post(form).then((e) => {
          console.log(e)
          this.delVisible = false
          this.batchVisible = false
          Toast.success(this.$t('成功'));
          this.$refs.multipleTable.clearSelection();
          this.seller_goods_list_action()
        }).catch((e) => {
          this.$refs.multipleTable.clearSelection();
          this.seller_goods_list_action()
        })
      }
      if (this.batchTitle == this.$t('批量上架')) {
        let form = {
          sellerGoodsId: e.toString(),
          isShelf: 1
        }
        api_goods_shelfBatch_post(form).then((e) => {
          console.log(e)
          this.delVisible = false
          this.batchVisible = false
          Toast.success(this.$t('成功'));
          this.$refs.multipleTable.clearSelection();
          this.seller_goods_list_action()
        }).catch((e) => {
          this.$refs.multipleTable.clearSelection();
          this.seller_goods_list_action()
        })
      }
      if (this.batchTitle == this.$t('批量下架')) {
        let form = {
          sellerGoodsId: e.toString(),
          isShelf: 0
        }
        api_goods_shelfBatch_post(form).then((e) => {
          console.log(e)
          this.delVisible = false
          this.batchVisible = false
          Toast.success(this.$t('成功'));
          this.$refs.multipleTable.clearSelection();
          this.seller_goods_list_action()
        }).catch((e) => {
          this.$refs.multipleTable.clearSelection();
          this.seller_goods_list_action()
        })
      }
    },
    api_goods_update(e) {
      let form = {
        percent: e.profitRatio,
        isShelf: e.isShelf,
        recTime: e.recTime,
        isCombo: e.isCombo ?? 0,
        discount: e.discountRatio || 0,
        startTime: e.discountStartTime,
        endTime: e.discountEndTime,
        sellerGoodsId: e.id,
      }
      api_goods_update_post(form).then((e) => {
        this.editVisible = false
        this.$refs.editCommodity.changeEditVisible(false)
        console.log(e)
        this.seller_goods_list_action()
      }).catch((e) => {
        this.seller_goods_list_action()
      })
    },

    seller_goods_list_action() {
      let data = {...this.form}
      data.categoryId = data.categoryId ? data.categoryId[data.categoryId.length - 1] : undefined
      seller_goods_list_action_post(data).then((e) => {
        this.promotional = e.data
        this.tableData = e.data.pageList
        this.form.totalElements = e.data.pageInfo.totalElements
        this.$nextTick(() => {//查找当前页选中的数据
          this.tableData.forEach((item) => {
            if (this.selectIdObj[item.id]) {
              this.$refs.multipleTable.toggleRowSelection(item);
            }
          });
        })
      })
    },

    // TODO: 搜索请求
    search() {
      console.log(this.form);
      this.form.pageNum = 1;
      this.getAllData();
    },
    // TODO: 重置搜索条件并且请求
    reset() {
      // this.$refs.searchForm.resetFields();
      this.form = {
        categoryId: undefined,
        isShelf: undefined,
        name: undefined,
        id: undefined,
      }
      this.getAllData();
    },
    // TODO: 每页几条,去请求获取数据
    handleSizeChange(val) {
      console.log(`每页 ${val} 条`);
      this.form.pageSize = val;
      this.getAllData();
    },
    // TODO: 当前第几页,去请求获取数据
    handleCurrentChange(val) {
      console.log(`当前页: ${val}`);
      this.form.pageNum = val;
      this.getAllData();
    },
    // TODO: 获取列表数据
    getAllData() {
      this.seller_goods_list_action()
      console.log("请求获取列表数据");
    },
  },
};
</script>

<style lang="scss" scoped>
.table-list {
  width: 100%;
  height: 100%;

  .merchandise-label {
    display: flex;
    justify-content: center;

    .merchandise-label-item {
      display: flex;
      justify-content: center;
      align-items: center;
      flex-direction: column;

      .button {
        width: 40px;
        height: 24px;
        display: flex;
        align-items: center;
      }

      .up {
        text-align: right;
        display: inline-block;
        margin-right: 10px;
        width: 100%;
        line-height: 24px;

        &.en {
        }
      }
    }
  }

  .search {
    padding: 20px 20px 0px 20px;
    background-color: #fff;
    margin-bottom: 10px;
    border-radius: 10px;
  }

  .table {
    padding: 20px;
    background-color: #fff;
    border-radius: 10px;

    ::v-deep .el-table__header-wrapper thead tr th {
    }
  }

  .detail {
    border: 1px solid #ccc;
    border-radius: 3px;
    margin-bottom: 20px;

    .header {
      line-height: 40px;
      padding-left: 10px;
      border-bottom: 1px solid #ccc;
    }

    .main-price {
      .item {
        display: flex;
        line-height: 30px;
        margin: 10px;
        justify-content: space-between;
        font-size: 16px;
        font-weight: 800;

        .name {
          font-weight: 800;
          font-size: 16px;
        }
      }

      .top {
        border-top: 1px solid #ccc;
        padding-top: 10px;
      }
    }
  }

  .btn {
    text-align: left;
    margin-bottom: 15px;
  }

  .order-top {
    border: 1px solid #ccc;
    border-radius: 3px;
    margin-bottom: 20px;

    .header {
      line-height: 40px;
      padding-left: 10px;
      border-bottom: 1px solid #ccc;
    }

    .main {
      .border {
        border-top: 1px solid #ccc;
      }

      &-content {
        display: flex;
        justify-content: space-between;
        margin: 0 10px;

        .left {
          width: 40%;

          .item {
            display: flex;
            line-height: 30px;
            margin: 10px;
            justify-content: space-between;
            font-size: 16px;
            font-weight: 800;
          }
        }

        .right {
          width: 40%;

          .item {
            display: flex;
            line-height: 30px;
            margin: 10px;
            justify-content: space-between;
            font-size: 16px;
            font-weight: 800;
          }
        }
      }
    }
  }

  .order-bottom {
    display: flex;
    justify-content: space-between;

    .content-left,
    .content-right {
      border: 1px solid #ccc;
      border-radius: 3px;
      margin-bottom: 20px;

      .header {
        line-height: 40px;
        padding-left: 10px;
        border-bottom: 1px solid #ccc;
      }
    }

    .content-left {
      width: calc(70% - 20px);
    }

    .content-right {
      width: 30%;

      .item {
        display: flex;
        line-height: 30px;
        margin: 10px;
        justify-content: space-between;
        font-size: 16px;
        font-weight: 800;

        .name {
          font-weight: 800;
          font-size: 16px;
        }
      }

      .top {
        border-top: 1px solid #ccc;
        padding-top: 10px;
      }
    }
  }

  //
  //::v-deep .el-dialog__header {
  //  font-weight: 700;
  //  color: #000000;
  //}
  //::v-deep .el-dialog__headerbtn .el-dialog__close {
  //  color: #333;
  //}
}


::v-deep .date .el-date-editor {
  width: 100%;
}

::v-deep {
  .el-table__body-wrapper, .el-table__header-wrapper {
    .cell {
      text-align: center;
    }
  }

  .el-image {
    max-width: 120px;
    max-height: 120px;

    img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
  }
}
</style>

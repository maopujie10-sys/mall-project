<template>
  <div class="settlement">
    <div
      class="settlement-commodity"
      v-for="(item, index) in checkProductPay"
      :key="index"
    >
      <!-- {{ checkProductPay }} -->
      <el-checkbox
        class="settlement-commodity-title"
        v-model="item.checkAll"
        :indeterminate="item.isIndeterminate"
        @change="handleCheckAllChange($event, index)"
      >
        {{ item.list[0].seller.name }}（{{ $t("message.home.totalOf") }}
        {{ item.checkList.length }} {{ $t("message.home.items") }}）
      </el-checkbox>
      <div class="settlement-commodity-group">
        <el-checkbox-group
          v-model="item.checkList"
          @change="handleCheckedChange($event, index)"
        >
          <div
            class="settlement-commodity-wrap"
            v-for="(childItem, childIndex) in item.list"
            :key="childIndex"
          >
            <el-checkbox
              :label="childItem.Identifier"
              class="settlement-commodity-checkbox flex-between"
            >
              <div class="settlement-commodity-item flex-start">
                <img
                  :src="
                    childItem.zoomImg ? childItem.zoomImg : childItem.imgUrl1
                  "
                  alt=""
                />
                <div
                  class="flex-start settlement-commodity-info"
                  :style="{ flexDirection: 'column', alignItems: 'flex-start' }"
                >
                  <div>
                    <h2 :title="childItem.name">{{ childItem.name }}</h2>
                    <p v-if="childItem.price">
                      ${{ numberFormat(childItem.price) }}
                    </p>
                    <p v-else>
                      ${{
                        numberFormat(
                          childItem.discountPrice ?? childItem.sellingPrice
                        )
                      }}
                    </p>
                  </div>
                  <div
                    class="settlement-commodity-info-attr"
                    v-if="childItem.checkAttrName"
                  >
                    <span>{{ $t("message.home.orderSpecification") }}:</span>
                    <span>{{ childItem.checkAttrName }}</span>
                  </div>
                </div>
              </div>
            </el-checkbox>
            <el-input-number
              v-model="childItem.checkTotal"
              size="mini"
              key="childItem.buyMin"
              @blur="changeNum(childItem,event)"
              :precision="0"
              :min="childItem.buyMin || 1"
              :max="maxNum"
            />
          </div>
        </el-checkbox-group>
      </div>
    </div>
  </div>
</template>

<script>
import { mapGetters, mapMutations } from "vuex";
import { numberFormat } from "@/util";

export default {
  name: "EsOrderList",
  data() {
    return {
      maxNum:0
    };
  },
  computed: {
    ...mapGetters("shopCart", ["checkProductPay"]),
  },
  created() {
    this.maxNum = Number(localStorage.getItem('maxBuy') || 500) 
    // console.log('this.maxNum ->', this.maxNum);
  },
  methods: {
    ...mapMutations("shopCart", ["updateCheckProductPay"]),
    changeNum(e) {
      console.log('e ->', e);
      if(e.checkTotal == 'undefined' || e.checkTotal == null || e.checkTotal == '' || e.checkTotal == 0){
         e.checkTotal = 1
        //  item.checkTotal = 1
      }
    },
    handleCheckAllChange(val, index) {
        // Identifier
      let copyCheckProductPayData = [...this.checkProductPay];
      // console.log(`copyCheckProductPayData ::->`, copyCheckProductPayData);
      copyCheckProductPayData[index].checkList = val
        ? this.checkProductPay[index].list.map((item) => item.Identifier)
        : [];
        // console.log('val ->', index);
      this.updateCheckProductPay(copyCheckProductPayData);
      this.isIndeterminate = false;
    },
    handleCheckedChange(value, index) {
      console.log("value,index ->", value, index);
      let copyCheckProductPayData = [...this.checkProductPay];
      // console.log("copyCheckProductPayData ->", copyCheckProductPayData);
      const checkedCount = value.length;
      // console.log('checkedCount ->', checkedCount);
      const all = copyCheckProductPayData[index].list.length;
      copyCheckProductPayData[index].checkAll = checkedCount === all;
      copyCheckProductPayData[index].isIndeterminate =
        checkedCount > 0 && checkedCount < all;
      this.updateCheckProductPay(copyCheckProductPayData);
    },
    handleCount(list) {
      let count = 0;
      console.log('list ->', list);
      list.forEach((item) => {
        count += item.checkTotal;
      });
      return count;
    },
    numberFormat,
  },
};
</script>

<style lang="scss">
html[dir="rtl"]{
  .settlement{
    .settlement-commodity-wrap .el-input-number{
      left: 24px;
      right: auto;
    }
    .settlement-commodity-item img{
      // margin-right: 5px;
      margin-left: 18px;
    }
    .el-checkbox__label{
      padding-right: 10px;
      padding-left: 0;
    }
  }
}
.settlement {
  .settlement-commodity-info-attr {
    color: #666;
    padding-top: 4px;
    font-size: 12px;
  }

  &-commodity {
    padding-bottom: 20px;

    &-title {
      margin-bottom: 11px;
      margin-top: 18px;

      .el-checkbox__label {
        font-weight: 500;
        font-size: 12px;
        color: var(--color-title);
      }
    }

    &-wrap {
      position: relative;

      .el-input-number {
        width: 100px;
        position: absolute;
        top: 30px;
        right: 24px;
      }

      .el-input-number__decrease,
      .el-input-number__increase {
        background-color: var(--color-white);
      }
    }

    &-wrap:first-child {
      .el-checkbox {
        border-top: 0;
      }
    }

    &-group {
      border: 1px solid var(--color-border);
      border-radius: 4px;
      padding: 10px;
    }

    &-item {
      img {
        width: 62px;
        height: 62px;
        margin-right: 18px;
        object-fit: contain;
      }
    }

    &-info {
      flex: 1;

      div {
        width: 100%;
      }

      h2 {
        font-weight: 400;
        font-size: 14px;
        color: var(--color-black);
        margin-bottom: 10px;
        max-width: 800px !important;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }

      p {
        font-weight: 500;
        font-size: 16px;
        color: var(--color-price);
      }
    }

    &-checkbox {
      display: flex !important;
      padding: 20px 10px;
      border-top: 1px solid var(--color-border);

      .el-checkbox__label {
        flex: 1;
      }
    }

    .el-checkbox__inner {
      border-radius: 50%;
    }
  }
}
</style>

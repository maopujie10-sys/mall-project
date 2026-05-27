<template>
  <div class="dashboard">
    <collection />
    <recharge />
    <withdraw />
  </div>
</template>
<script>
import collection from "./collection";
import recharge from "./recharge";
import withdraw from "./withdraw";
export default {
  components: {
    collection,
    recharge,
    withdraw,
  },
};
</script>
<style lang="scss">
html[dir="rtl"] {
  .dashboard {
    padding-left: 0;
    padding-right: 50px;
  }
}
.dashboard {
  flex: 1;
  padding: 20px 0 0 50px;
  display: flex;
}

.box-btn {
  background-color: #fafafa;
  border: 1px solid #eeeeee;
  border-radius: 4px;
  height: 85px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #333;
  user-select: none;
  cursor: pointer;
  transition-duration: 0.3s;

  &:hover {
    box-shadow: 0 1px 2px 1px rgba(0, 0, 0, 0.05);
  }

  .icon {
    width: 32px;
    height: 32px;
    margin-top: 8px;
    transform: rotate(180deg);
  }
}

.wallet-dialog {
  .el-dialog__body {
    padding: 20px 37px 37px;
  }

  .network-select {
    position: relative;

    .right {
      position: absolute;
      right: 0;
      top: 0;
      height: 50px;
      display: flex;
      align-items: center;
    }

    .el-radio-group {
      .el-radio-button {
        position: relative;

        .el-radio-button__inner {
          border: 1px solid #dddddd;
          border-radius: 4px;
          font-weight: 400;
          color: #999;
          box-shadow: none !important;
          padding: 0 32px;
          height: 44px;
          display: flex;
          align-items: center;
        }

        &.is-active {
          .el-radio-button__inner {
            border: 1px solid var(--color-main);
            background-color: #fff;
            color: var(--color-main);
          }

          &:after {
            content: "";
            background-image: url("~@/assets/image/btn-selected.svg");
            width: 23px;
            height: 23px;
            position: absolute;
            right: 0;
            bottom: 0;
            z-index: 1;
          }
        }

        + .el-radio-button {
          margin-left: 15px;
        }
      }
    }
  }

  .qr-code {
    display: flex;
    align-items: center;
    margin-top: 8px;
    margin-bottom: 18px;

    .el-button {
      margin-left: 36px;
    }
  }

  .wallet-address {
    position: relative;

    .copy-btn {
      position: absolute;
      top: 0;
      bottom: 0;
      right: 15px;
      z-index: 1;
      color: #1d91ff;
      user-select: none;
      display: block;
      cursor: pointer;

      &.disabled {
         color: #aaa;
         cursor: default;
      }
    }
  }

  .image-uploader {
    .el-upload {
      border-radius: 6px;
      cursor: pointer;
      position: relative;
      overflow: hidden;
      height: 96px;

      &:hover {
        border-color: #409eff;
      }
    }

    .image {
      width: 96px;
      height: 96px;
      display: block;
    }

    .label {
      width: 93px;
      text-align: center;
      margin-top: -15px;
      font-size: 12px;
      color: #999999;
    }
  }

  .submit-btn {
    width: 100%;
    height: 44px;
    background-color: var(--color-main);
    border-radius: 4px;
    color: #fff;
    font-size: 16px;
    font-weight: 500;
  }
}
</style>

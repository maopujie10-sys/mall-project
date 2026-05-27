
import { copyTextToClipboard, numberFormat } from '@/util';
import { ES_REMIND_ORDER } from '@/common';
import { mapActions, mapGetters, mapMutations } from 'vuex';
import { getOrderStatusLable } from '@/util/shop';
import OrderPaymentDialog from '@/page/userInfo/my-order/components/order-payment-dialog';
import OrderCancelDialog from '@/page/userInfo/my-order/components/order-cancel-dialog';
import OrderLogisticsDialog from '@/page/userInfo/my-order/components/order-logistics-dialog';

export default {

    components: {
        OrderPaymentDialog,
        OrderCancelDialog,
        OrderLogisticsDialog
    },

    mounted() {
        // console.log(this.currentOrder.id)
    },

    data() {
        return {
            orderId: this.data?.id || this.$route.query?.orderId,
            currentOrderInfo: {},
            loading: false,
            logisticsDialogVisible: false,
            paymentDialogVisible: false,
            cancelDialogVisible: false,
            queryButton: {
                key: "queryButton",
                text: this.$t('message.home.Checkorder'),
                func: () => {
                    localStorage.setItem('orderStatus', this.data.sellerStatus);
                    this.$router.push({ name: 'order-detail', query: { orderId: this.orderId } })
                }
            },
            payButton: {
                // payment
                key: "payButton",
                text: this.$t('message.home.order.payment'),
                activity: true,
                func: () => {
                    this.paymentDialogVisible = true
                }
            },
            sendInfoButton: {
                key: "sendInfoButton",
                text: this.$t('message.home.RemindShip'),
                func: this.remindOrder,

                // func: () => { }
            },

            confirmButton: {
                key: "confirmButton",
                text: this.$t('message.home.order.confirm' /**确认收货 */),
                func: this.receiptOrder
            },
            cancelButton: {
                key: "cancelButton",
                text: this.$t('message.home.cancelOrder',/**取消订单 */),
                func: () => {
                    this.cancelDialogVisible = true
                }
            },
            returnPayButton: {
                key: "returnPayButton",
                text: this.$t('message.home.returnApply',/**退款申请 */),
                func: () => {
                    this.$router.push({ name: 'order-return', params: { currentOrder: this.currentOrderInfo } })
                }
            },
            reBuyButton: {
                key: "reBuyButton",
                text: this.$t('message.home.rebuy'),
                func: () => { }
            },
            evaluateButton: {
                key: "evaluateButton",
                text: this.$t('message.home.order.evaluate'),
                func: () => {
                    this.$router.push({ name: 'order-evaluation', query: { orderId: this.currentOrderInfo.id } })
                }
            },
            queryLogisticsButton: {
                key: "queryLogisticsButton",
                text: this.$t('message.home.order.logistics'),
                func: () => {
                    this.logisticsDialogVisible = true
                }
            }
        }
    },
    computed: {
        ...mapGetters('order', ['remindList']),
    },
    methods: {
        ...mapActions({
            requestOrderCancel: 'order/requestOrderCancel',
            requestOrderReceipt: 'order/requestOrderReceipt',
            requestOrderReturn: 'order/requestOrderReturn',
        }),
        ...mapMutations({
            updateRemindList: 'order/updateRemindList'
        }),
        closePayDialog(){
            this.paymentDialogVisible=false
        },
        goBack() {
            this.$router.go(-1)
        },
        remindOrder() {
            const orderId = this.orderId
            if (!this.remindList.includes(orderId)) {
                this.$confirm(this.$t('message.home.remindContent'), this.$t('message.home.remindTitle'), {
                    confirmButtonText: this.$t('message.home.btnSure'),
                    cancelButtonText: this.$t('message.home.cancel'),
                    type: 'warning',
                }).then(() => {
                    this.remindLoading = true
                    setTimeout(() => {
                        this.remindList.push(orderId);
                        this.updateRemindList(this.remindList);
                        localStorage.setItem(ES_REMIND_ORDER, JSON.stringify(this.remindList))
                        this.$notify({
                            title: this.$t("message.home.successTips"),
                            message: this.$t("message.home.remindSuccess"),
                            type: "success",
                        });
                        this.remindLoading = false
                    }, 1000)
                })
            } else {
                this.$message.warning(this.$t('message.home.remindRepeat'))
            }
        },
        // 确认收获
        receiptOrder() {
            this.$confirm(this.$t('message.home.confirmReceiveGoods'), this.$t('message.home.hint'), {
                confirmButtonText: this.$t('message.home.confirm'),
                cancelButtonText: this.$t('message.home.cancel'),
                type: 'warning',
            })
                .then(async () => {
                    try {
                        this.receiptLoading = true;
                        await this.requestOrderReceipt({ orderId: this.orderId });
                        this.refresh && this.refresh();
                        this.$notify({
                            title: this.$t('message.home.successTips'),
                            message: this.$t('message.home.operationSuccess'),
                            type: 'success',
                        });
                        this.closeDetails()
                    } finally {
                        this.receiptLoading = false;
                    }
                })
                .catch(() => { });
        },
        copy() {
            copyTextToClipboard(this.orderId);
            this.$notify({
                title: this.$t('message.home.successTips'),
                message: this.$t('message.home.copySuccess'),
                type: 'success',
            });
        },
        numberFormat,
        getOrderStatusLable,
    }
}
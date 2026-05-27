package util;

import com.aliyun.oss.OSS;
import com.aliyun.oss.OSSClientBuilder;
import com.aliyun.oss.model.Bucket;
import com.aliyun.oss.model.CreateBucketRequest;
import com.aliyun.oss.model.PutObjectRequest;
import com.aliyun.oss.model.PutObjectResult;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.multipart.MultipartFile;

import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.Date;
import java.util.UUID;

public class AliOssUtil {

    private static  OSS client;
    private static   String endpoint;
    private static  String accessKeyId;
    private static String accessKeySecret;
    private static String bucketName;

    /**
     * 实现上传图片到OSS
     */
    public static String uploadImg(MultipartFile multipartFile,String aliendpoint,String aliaccessKeyId,String aliaccessKeySecret,String alibucketName) throws IOException {
        endpoint = aliendpoint;
        accessKeyId = aliaccessKeyId;
        accessKeySecret = aliaccessKeySecret;
        bucketName = alibucketName;
        // 获取上传的文件的输入流
        InputStream inputStream = multipartFile.getInputStream();
        // 避免文件覆盖
        String originalFilename = multipartFile.getOriginalFilename();
        String fileName = UUID.randomUUID().toString() + originalFilename.substring(originalFilename.lastIndexOf("."));
        //上传文件到 OSS
        OSS client = new OSSClientBuilder().build(endpoint, accessKeyId, accessKeySecret);
        client.putObject(bucketName, fileName, inputStream);
        //文件访问路径
        String url = endpoint.split("//")[0] + "//" + bucketName + "." + endpoint.split("//")[1] + "/" + fileName;
        // 关闭ossClient
        client.shutdown();
        return url;// 把上传到oss的路径返回
    }


    /**
     * 创建储存空间名称
     * @param name 创建存储空间名称
     * @return
     */
    public static boolean create(String name) {
        CreateBucketRequest createBucketRequest = new CreateBucketRequest(name);
        Bucket bucket = client.createBucket(createBucketRequest);
        return bucket!=null;
    }

    /**
     * 实现文件上传
     * @param bucket 存储空间名称
     * @param obj 存储对象名称，带文件后缀
     * @param data 文件内容
     * @return
     */
    public static boolean upload(String bucket,String obj, byte[] data) {
        PutObjectRequest request = new PutObjectRequest(bucket, obj, new ByteArrayInputStream(data));
        request.setProcess("true");
        PutObjectResult result=client.putObject(request);
        return result.getResponse().getStatusCode()==200;
    }

    /**
     * 创建访问链接
     * @param bucket 存储空间名称
     * @param obj 存储对象名称，带文件名后缀
     * @param etime 访问地址的失效时间
     * @return 访问地址
     */
    public static String createUrl(String bucket, String obj, Date etime){
        return client.generatePresignedUrl(bucket, obj, etime).toString();
    }

    /**
     * 删除文件
     * @param bucket 存储空间名称
     * @param obj 存储对象名称，带文件后缀
     */
    public static void deFile(String bucket,String obj){
        client.deleteObject(bucket, obj);
    }


}

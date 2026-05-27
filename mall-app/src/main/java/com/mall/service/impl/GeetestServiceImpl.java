package com.mall.service.impl;

import com.mall.service.GeetestService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.net.HttpURLConnection;
import java.net.InetAddress;
import java.net.Socket;
import java.net.URL;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;

@Service
public class GeetestServiceImpl implements GeetestService {

    private static final Logger log = LoggerFactory.getLogger(GeetestServiceImpl.class);

    protected final String verName = "3.3.0";
    protected final String sdkLang = "java";
    protected final String apiUrl = "http://api.geetest.com";
    protected final String baseUrl = "api.geetest.com";
    protected final String registerUrl = "/register.php";
    protected final String validateUrl = "/validate.php";
    public boolean debugCode = false;

    @Override
    public Map<String, String> preProcess(Map<String, String> data) {
        try {
            String userId = data.get("user_id");
            String geetestId = data.get("geetest_id");
            String geetestKey = data.get("geetest_key");

            String getUrl = this.apiUrl + this.registerUrl + "?";
            String param = "gt=" + geetestId;
            if (userId != null) {
                param = param + "&user_id=" + userId;
            }

            String resultStr = readContentFromGet(getUrl + param);

            if (resultStr != null && 32 == resultStr.length()) {
                return getSuccessPreProcessRes(md5Encode(resultStr + geetestKey), geetestId);
            } else {
                return getFailPreProcessRes(geetestId);
            }
        } catch (Throwable t) {
            log.error("Geetest preProcess error", t);
        }
        return null;
    }

    @Override
    public int enhencedValidateRequest(Map<String, String> data) {
        String userId = data.get("user_id");
        String challenge = data.get("challenge");
        String validate = data.get("validate");
        String seccode = data.get("seccode");
        String geetestKey = data.get("geetest_key");

        if (!resquestIsLegal(challenge, validate, seccode)) {
            return 0;
        }

        String host = baseUrl;
        String path = validateUrl;
        int port = 80;
        String query = String.format("seccode=%s&sdk=%s", seccode, (this.sdkLang + "_" + this.verName));

        if (userId != null && !userId.isEmpty()) {
            query = query + "&user_id=" + userId;
        }

        try {
            if (validate.length() <= 0) {
                return 0;
            }
            if (!checkResultByPrivate(challenge, validate, geetestKey)) {
                return 0;
            }
            String response = postValidate(host, path, query, port);
            if (response.equals(md5Encode(seccode))) {
                return 1;
            } else {
                return 0;
            }
        } catch (Exception e) {
            log.error("Geetest enhencedValidateRequest error", e);
        }
        return 0;
    }

    @Override
    public int failbackValidateRequest(Map<String, String> data) {
        String challenge = data.get("challenge");
        String validate = data.get("validate");
        String seccode = data.get("seccode");

        if (!resquestIsLegal(challenge, validate, seccode)) {
            return 0;
        }

        String[] validateStr = validate.split("_");
        String encodeAns = validateStr[0];
        String encodeFullBgImgIndex = validateStr[1];
        String encodeImgGrpIndex = validateStr[2];

        int decodeAns = decodeResponse(challenge, encodeAns);
        int decodeFullBgImgIndex = decodeResponse(challenge, encodeFullBgImgIndex);
        int decodeImgGrpIndex = decodeResponse(challenge, encodeImgGrpIndex);

        return validateFailImage(decodeAns, decodeFullBgImgIndex, decodeImgGrpIndex);
    }

    @Override
    public String getVersionInfo() {
        return this.verName;
    }

    // ========== private helpers ==========

    private Map<String, String> getFailPreProcessRes(String geetestId) {
        Long rnd1 = Math.round(Math.random() * 100);
        Long rnd2 = Math.round(Math.random() * 100);
        String md5Str1 = md5Encode(rnd1 + "");
        String md5Str2 = md5Encode(rnd2 + "");
        String challenge = md5Str1 + md5Str2.substring(0, 2);

        Map<String, String> ret = new HashMap<>();
        ret.put("success", "0");
        ret.put("gt", geetestId);
        ret.put("challenge", challenge);
        return ret;
    }

    private Map<String, String> getSuccessPreProcessRes(String challenge, String geetestId) {
        Map<String, String> ret = new HashMap<>();
        ret.put("success", "1");
        ret.put("gt", geetestId);
        ret.put("challenge", challenge);
        return ret;
    }

    private int validateFailImage(int ans, int fullBgIndex, int imgGrpIndex) {
        final int thread = 3;
        String fullBgName = md5Encode(fullBgIndex + "").substring(0, 9);
        String bgName = md5Encode(imgGrpIndex + "").substring(10, 19);
        String answerDecode = "";
        for (int i = 0; i < 9; i++) {
            if (i % 2 == 0) {
                answerDecode += fullBgName.charAt(i);
            } else {
                answerDecode += bgName.charAt(i);
            }
        }
        String xDecode = answerDecode.substring(4);
        int xInt = Integer.valueOf(xDecode, 16);
        int result = xInt % 200;
        if (result < 40) {
            result = 40;
        }
        if (Math.abs(ans - result) <= thread) {
            return 1;
        } else {
            return 0;
        }
    }

    private int decodeResponse(String challenge, String string) {
        if (string.length() > 100) {
            return 0;
        }
        int[] shuzi = new int[]{1, 2, 5, 10, 50};
        String chongfu = "";
        Map<String, Integer> key = new HashMap<>();
        int count = 0;
        for (int i = 0; i < challenge.length(); i++) {
            String item = challenge.charAt(i) + "";
            if (chongfu.contains(item)) {
                continue;
            } else {
                int value = shuzi[count % 5];
                chongfu += item;
                count++;
                key.put(item, value);
            }
        }
        int res = 0;
        for (int j = 0; j < string.length(); j++) {
            res += key.get(string.charAt(j) + "");
        }
        res = res - decodeRandBase(challenge);
        return res;
    }

    private int decodeRandBase(String challenge) {
        String base = challenge.substring(32, 34);
        ArrayList<Integer> tempArray = new ArrayList<>();
        for (int i = 0; i < base.length(); i++) {
            char tempChar = base.charAt(i);
            Integer tempAscii = (int) tempChar;
            Integer result = (tempAscii > 57) ? (tempAscii - 87) : (tempAscii - 48);
            tempArray.add(result);
        }
        return tempArray.get(0) * 36 + tempArray.get(1);
    }

    private String readContentFromGet(String getURL) throws Exception {
        URL getUrl = new URL(getURL);
        HttpURLConnection connection = (HttpURLConnection) getUrl.openConnection();
        connection.setConnectTimeout(2000);
        connection.setReadTimeout(2000);
        connection.connect();

        StringBuilder sBuffer = new StringBuilder();
        java.io.InputStream inStream = connection.getInputStream();
        byte[] buf = new byte[1024];
        for (int n; (n = inStream.read(buf)) != -1; ) {
            sBuffer.append(new String(buf, 0, n, "UTF-8"));
        }
        inStream.close();
        connection.disconnect();
        return sBuffer.toString();
    }

    protected String postValidate(String host, String path, String data, int port) throws Exception {
        String response = "error";
        InetAddress addr = InetAddress.getByName(host);
        Socket socket = new Socket(addr, port);
        BufferedWriter wr = new BufferedWriter(new OutputStreamWriter(socket.getOutputStream(), "UTF8"));
        wr.write("POST " + path + " HTTP/1.0\r\n");
        wr.write("Host: " + host + "\r\n");
        wr.write("Content-Type: application/x-www-form-urlencoded\r\n");
        wr.write("Content-Length: " + data.length() + "\r\n");
        wr.write("\r\n");
        wr.write(data);
        wr.flush();

        BufferedReader rd = new BufferedReader(new InputStreamReader(socket.getInputStream(), "UTF-8"));
        String line;
        while ((line = rd.readLine()) != null) {
            response = line;
        }
        wr.close();
        rd.close();
        socket.close();
        return response;
    }

    private boolean objIsEmpty(Object gtObj) {
        if (gtObj == null) return true;
        if (gtObj.toString().trim().length() == 0) return true;
        return false;
    }

    private boolean resquestIsLegal(String challenge, String validate, String seccode) {
        if (objIsEmpty(challenge)) return false;
        if (objIsEmpty(validate)) return false;
        if (objIsEmpty(seccode)) return false;
        return true;
    }

    protected boolean checkResultByPrivate(String challenge, String validate, String privateKey) {
        String encodeStr = md5Encode(privateKey + "geetest" + challenge);
        return validate.equals(encodeStr);
    }

    private String md5Encode(String plainText) {
        String reMd5 = "";
        try {
            MessageDigest md = MessageDigest.getInstance("MD5");
            md.update(plainText.getBytes());
            byte b[] = md.digest();
            StringBuffer buf = new StringBuffer("");
            for (int offset = 0; offset < b.length; offset++) {
                int i = b[offset];
                if (i < 0) i += 256;
                if (i < 16) buf.append("0");
                buf.append(Integer.toHexString(i));
            }
            reMd5 = buf.toString();
        } catch (NoSuchAlgorithmException e) {
            log.error("MD5 error", e);
        }
        return reMd5;
    }
}

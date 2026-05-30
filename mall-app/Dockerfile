# =============================================
# Friday AI OS — Mall API 多阶段构建
# 无需本地安装 Maven，Docker 内自动编译
# =============================================

# ---- Stage 1: 编译 ----
FROM maven:3.9-eclipse-temurin-17 AS builder
WORKDIR /build
COPY pom.xml .
RUN mvn dependency:go-offline -B -q || true
COPY src ./src
RUN mvn clean package -DskipTests -B -q

# ---- Stage 2: 运行 ----
FROM eclipse-temurin:17-jre
WORKDIR /app
RUN useradd -m -s /bin/bash appuser && \
    mkdir -p /app/logs /app/uploads && \
    chown -R appuser:appuser /app
COPY --from=builder /build/target/*.jar app.jar
USER appuser
EXPOSE 8080
ENTRYPOINT ["java", "-Xms512m", "-Xmx1024m", "-XX:+UseG1GC", "-XX:MaxGCPauseMillis=200", "-jar", "app.jar", "--spring.profiles.active=prod"]

FROM eclipse-temurin:17-jdk
WORKDIR /app
RUN mkdir -p /app/logs /app/uploads
COPY target/mall-app.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-Xms512m", "-Xmx1024m", "-XX:+UseG1GC", "-XX:MaxGCPauseMillis=200", "-jar", "app.jar", "--spring.profiles.active=prod"]

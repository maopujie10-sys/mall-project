package project.invest.expert;

import kernel.web.Page;
import project.invest.expert.model.Expert;

import java.util.List;
import java.util.Map;

public interface AdminExpertService {

    Page pagedQuery(int pageNo, int pageSize);

    void save(Expert expert);

    Expert findById(String id);

    void update(Expert expert);

    void delete(Expert expert);

    void deleteformhref(String id);

    Page pagedQueryCategory(int pageNo, int pageSize);

    void categorydelete(String id);

    void addformcategory(String sort, String className, String lang);

    void addformlist(String sort, String title, String href, String classId);

    List<Map<String, Object>> queryClass();
}
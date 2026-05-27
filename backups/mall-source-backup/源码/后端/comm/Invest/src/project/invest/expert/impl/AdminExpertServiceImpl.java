package project.invest.expert.impl;

import kernel.util.DateUtils;
import kernel.util.UUIDGenerator;
import kernel.web.Page;
import kernel.web.PagedQueryDao;
import org.apache.commons.lang3.StringUtils;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.orm.hibernate5.support.HibernateDaoSupport;
import project.invest.expert.AdminExpertService;
import project.invest.expert.model.Expert;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class AdminExpertServiceImpl extends HibernateDaoSupport implements AdminExpertService {

    private PagedQueryDao pagedQueryDao;

    public PagedQueryDao getPagedQueryDao() {
        return pagedQueryDao;
    }

    public JdbcTemplate getJdbcTemplate() {
        return jdbcTemplate;
    }

    public void setJdbcTemplate(JdbcTemplate jdbcTemplate) {
        this.jdbcTemplate = jdbcTemplate;
    }

    private JdbcTemplate jdbcTemplate;

    @Override
    public Page pagedQuery(int pageNo, int pageSize) {
        StringBuffer queryString = new StringBuffer(" SELECT s.*,f.CLASS_NAME,f.LANG FROM T_MALL_FOOTER_HREF s,T_FOOTER_HREF_CLASS f WHERE s.CLASS_ID = f.UUID ORDER BY s.SORT desc ");
        Map<String, Object> parameters = new HashMap();
        Page page = this.pagedQueryDao.pagedQuerySQL(pageNo, pageSize, queryString.toString(), parameters);
        return page;
    }


    public Page pagedQueryCategory(int pageNo, int pageSize) {
        StringBuffer queryString = new StringBuffer(" SELECT * FROM T_FOOTER_HREF_CLASS  ORDER BY SORT desc ");
        Map<String, Object> parameters = new HashMap();
        Page page = this.pagedQueryDao.pagedQuerySQL(pageNo, pageSize, queryString.toString(), parameters);
        return page;
    }

    @Override
    public void categorydelete(String id) {
        String SQL = "DELETE FROM T_FOOTER_HREF_CLASS  WHERE UUID = ?";
        int update = jdbcTemplate.update(SQL,id);
    }

    @Override
    public void addformcategory(String sort, String className, String lang) {
        String SQL = "INSERT INTO `mall`.`T_FOOTER_HREF_CLASS` (`UUID`, `CLASS_NAME`, `LANG`, `SORT`) VALUES (?, ?, ?, ?);";
        int update = jdbcTemplate.update(SQL,UUIDGenerator.getUUID(),className,lang,sort);
    }

    @Override
    public void addformlist(String sort, String title, String href, String classId) {
        String SQL = "INSERT INTO `mall`.`T_MALL_FOOTER_HREF` (`UUID`, `TITLE`, `HREF`, `CLASS_ID`, `SORT`, `CREATE_TIME`) VALUES (?,?,?,?,?, NOW())";
        int update = jdbcTemplate.update(SQL,UUIDGenerator.getUUID(),title,href,classId,sort);
    }

    @Override
    public List<Map<String, Object>> queryClass() {
        String sql = "select * FROM T_FOOTER_HREF_CLASS";
        return jdbcTemplate.queryForList(sql);
    }

    @Override
    public void save(Expert expert) {
        this.getHibernateTemplate().save(expert);
    }

    @Override
    public Expert findById(String id) {
        return getHibernateTemplate().get(Expert.class, id);
    }

    @Override
    public void update(Expert expert) {
       this.getHibernateTemplate().update(expert);
    }

    @Override
    public void delete(Expert expert) {
        this.getHibernateTemplate().delete(expert);
    }

    @Override
    public void deleteformhref(String id) {
        String SQL = "DELETE FROM T_MALL_FOOTER_HREF  WHERE UUID = ?";
        int update = jdbcTemplate.update(SQL,id);

    }


    public void setPagedQueryDao(PagedQueryDao pagedQueryDao) {
        this.pagedQueryDao = pagedQueryDao;
    }
}
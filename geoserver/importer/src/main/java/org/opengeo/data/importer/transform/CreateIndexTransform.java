package org.opengeo.data.importer.transform;

import java.sql.Connection;
import java.sql.Statement;
import java.util.logging.Level;
import org.geoserver.catalog.DataStoreInfo;
import org.geotools.data.DataAccess;
import org.geotools.data.Transaction;
import org.geotools.jdbc.JDBCDataStore;
import org.opengeo.data.importer.ImportData;
import org.opengeo.data.importer.ImportItem;

/**
 *
 * @author Ian Schneider <ischneider@opengeo.org>
 */
public class CreateIndexTransform extends AbstractVectorTransform implements PostVectorTransform {
    
    private static final long serialVersionUID = 1L;
    
    private String field;
    
    public CreateIndexTransform(String field) {
        this.field = field;
    }

    public String getField() {
        return field;
    }

    public void setField(String field) {
        this.field = field;
    }
    
    public void apply(ImportItem item, ImportData data) throws Exception {
        DataStoreInfo storeInfo = (DataStoreInfo) item.getTask().getStore();
        DataAccess store = storeInfo.getDataStore(null);
        if (store instanceof JDBCDataStore) {
            createIndex( item, (JDBCDataStore) store);
        } else {
            item.addImportMessage(Level.WARNING, "Cannot create index on non database target. Not a big deal.");
        }
    }
    
    private void createIndex(ImportItem item, JDBCDataStore store) throws Exception {
        try {
            //@todo another way to do this??
            //if ("PostGISDialect".equals(store.getSQLDialect().getClass().getSimpleName())) {
                Connection conn = null;
                Statement stmt = null;
                try {
                    conn = store.getConnection(Transaction.AUTO_COMMIT);
                    stmt = conn.createStatement();
                    String tableName = item.getLayer().getResource().getNativeName();
                    String indexName = "\"" + tableName + "_" + field + "\"";
                    stmt.execute("CREATE INDEX " + indexName + " ON " + tableName + "(\"" + field + "\")");
                } finally {
                    store.closeSafe(stmt);
                    store.closeSafe(conn);
                }
            //}
        } finally {
            store.dispose();
        }
    }
    
}
